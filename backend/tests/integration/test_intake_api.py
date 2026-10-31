import io
import pytest
from httpx import ASGITransport, AsyncClient

from sqlalchemy import text
from backend.app.core.database import AsyncSessionLocal, Base, engine
from backend.app.main import app
from backend.app.services.auth_service import seed_initial_users


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Ensure tables exist and seed initial personas."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await seed_initial_users(session)
    yield
    await engine.dispose()


@pytest.fixture(autouse=True)
async def clean_documents():
    """Clean up documents table before and after each test for idempotency."""
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM document_permissions"))
        await session.execute(text("DELETE FROM documents"))
        await session.commit()
    yield
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM document_permissions"))
        await session.execute(text("DELETE FROM documents"))
        await session.commit()


async def get_auth_token(client: AsyncClient, username: str = "regular_user") -> str:
    passwords = {
        "admin_user": "AdminPass123!",
        "editor_user": "EditorPass123!",
        "regular_user": "UserPass123!",
        "auditor_user": "AuditorPass123!",
    }
    pwd = passwords.get(username, "UserPass123!")
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": pwd},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_upload_supported_formats_tc_up_01():
    """
    TC-UP-01: Upload PDF, DOCX, and TXT files.
    Verify 201 Created, status QUEUED, and valid SHA-256 returned.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Valid PDF file
        pdf_content = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
        resp_pdf = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("sample_report.pdf", io.BytesIO(pdf_content), "application/pdf")},
        )
        assert resp_pdf.status_code == 201
        data_pdf = resp_pdf.json()
        assert data_pdf["file_type"] == "pdf"
        assert data_pdf["status"] == "QUEUED"
        assert len(data_pdf["file_hash"]) == 64

        # 2. Valid DOCX file (OpenXML Zip signature PK\x03\x04)
        docx_content = b"PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!" + b"A" * 100
        resp_docx = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("spec_doc.docx", io.BytesIO(docx_content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        )
        assert resp_docx.status_code == 201
        data_docx = resp_docx.json()
        assert data_docx["file_type"] == "docx"
        assert data_docx["status"] == "QUEUED"

        # 3. Valid TXT file
        txt_content = b"AICMS Project Overview\nThis is a standard UTF-8 text document for testing."
        resp_txt = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("notes.txt", io.BytesIO(txt_content), "text/plain")},
        )
        assert resp_txt.status_code == 201
        data_txt = resp_txt.json()
        assert data_txt["file_type"] == "txt"
        assert data_txt["status"] == "QUEUED"


@pytest.mark.asyncio
async def test_file_size_limit_rejection_tc_up_02():
    """
    TC-UP-02: Files exceeding 20 MB are rejected with 413 Payload Too Large.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        # Create virtual content exceeding 20 MB (20 MB + 1 KB)
        oversized_content = b"%PDF-1.4\n" + b"X" * (20 * 1024 * 1024 + 1024)
        resp = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("oversized.pdf", io.BytesIO(oversized_content), "application/pdf")},
        )
        assert resp.status_code == 413
        data = resp.json()
        assert data["code"] == "FILE_TOO_LARGE"
        assert "20MB" in data["message"]


@pytest.mark.asyncio
async def test_duplicate_document_rejection_tc_up_03():
    """
    TC-UP-03: Uploading identical file twice produces 409 Conflict on second attempt.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        unique_txt = b"Unique content for SHA-256 deduplication test - timestamp 20261031"

        # First upload: succeeds with 201
        resp1 = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("first_upload.txt", io.BytesIO(unique_txt), "text/plain")},
        )
        assert resp1.status_code == 201
        first_id = resp1.json()["document_id"]

        # Second upload with identical bytes: must fail with 409 Conflict
        resp2 = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("renamed_duplicate.txt", io.BytesIO(unique_txt), "text/plain")},
        )
        assert resp2.status_code == 409
        data2 = resp2.json()
        assert data2["code"] == "DUPLICATE_DOCUMENT"
        assert str(first_id) in data2["message"]


@pytest.mark.asyncio
async def test_unsupported_format_rejection_tc_up_04():
    """
    TC-UP-04: Unsupported file formats (e.g. .csv, .zip, .exe) rejected with 400.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        # 1. CSV
        resp_csv = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("table.csv", io.BytesIO(b"id,name\n1,alice"), "text/csv")},
        )
        assert resp_csv.status_code == 400
        assert resp_csv.json()["code"] == "UNSUPPORTED_FORMAT"

        # 2. ZIP
        resp_zip = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("archive.zip", io.BytesIO(b"PK\x03\x04archive"), "application/zip")},
        )
        assert resp_zip.status_code == 400
        assert resp_zip.json()["code"] == "UNSUPPORTED_FORMAT"


@pytest.mark.asyncio
async def test_disguised_malicious_file_rejection_tc_sec_04():
    """
    TC-SEC-04: Disguised files (wrong magic bytes) rejected with 400 INVALID_FILE_SIGNATURE.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Windows Executable (.exe) disguised as .pdf (starts with MZ)
        fake_pdf_exe = b"MZ\x90\x00\x03\x00\x00\x00This is an executable payload"
        resp_fake_pdf = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("malicious.pdf", io.BytesIO(fake_pdf_exe), "application/pdf")},
        )
        assert resp_fake_pdf.status_code == 400
        assert resp_fake_pdf.json()["code"] == "INVALID_FILE_SIGNATURE"

        # 2. Plain text file disguised as .pdf (does not start with %PDF-)
        plain_as_pdf = b"Hello, this is just text claiming to be a PDF"
        resp_bad_pdf = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("not_really.pdf", io.BytesIO(plain_as_pdf), "application/pdf")},
        )
        assert resp_bad_pdf.status_code == 400
        assert resp_bad_pdf.json()["code"] == "INVALID_FILE_SIGNATURE"

        # 3. Disguised binary in .txt file (null bytes)
        binary_txt = b"Some text\x00\x00\x00Binary payload"
        resp_bad_txt = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("binary_notes.txt", io.BytesIO(binary_txt), "text/plain")},
        )
        assert resp_bad_txt.status_code == 400
        assert resp_bad_txt.json()["code"] == "INVALID_FILE_SIGNATURE"


@pytest.mark.asyncio
async def test_document_lifecycle_status_and_authz_isolation():
    """
    Verify status endpoint and document authorization isolation (ADR-002, ADR-005).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Regular user uploads a document
        user_token = await get_auth_token(client, username="regular_user")
        user_headers = {"Authorization": f"Bearer {user_token}"}

        content = b"Hello from private document owner - verification"
        upload_resp = await client.post(
            "/api/v1/documents/upload",
            headers=user_headers,
            files={"file": ("private_doc.txt", io.BytesIO(content), "text/plain")},
        )
        assert upload_resp.status_code == 201
        doc_id = upload_resp.json()["document_id"]

        # 2. Status endpoint returns QUEUED
        status_resp = await client.get(
            f"/api/v1/documents/{doc_id}/status",
            headers=user_headers,
        )
        assert status_resp.status_code == 200
        assert status_resp.json()["status"] == "QUEUED"

        # 3. Another user (e.g. editor_user) tries to access this private document
        # Must return 404 Not Found to prevent existence leakage (ADR-005)
        editor_token = await get_auth_token(client, username="editor_user")
        editor_headers = {"Authorization": f"Bearer {editor_token}"}

        leak_resp = await client.get(
            f"/api/v1/documents/{doc_id}",
            headers=editor_headers,
        )
        assert leak_resp.status_code == 404
        assert leak_resp.json()["code"] == "NOT_FOUND"

        # 4. Admin user CAN access any document
        admin_token = await get_auth_token(client, username="admin_user")
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        admin_resp = await client.get(
            f"/api/v1/documents/{doc_id}",
            headers=admin_headers,
        )
        assert admin_resp.status_code == 200
        assert admin_resp.json()["id"] == doc_id
