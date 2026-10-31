import io
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from backend.app.core.config import settings
from backend.app.core.database import AsyncSessionLocal, Base, engine
from backend.app.main import app
from backend.app.services.auth_service import seed_initial_users


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await seed_initial_users(session)
    yield
    await engine.dispose()


@pytest.fixture(autouse=True)
async def clean_documents():
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM document_vectors"))
        await session.execute(text("DELETE FROM document_metadata"))
        await session.execute(text("DELETE FROM document_permissions"))
        await session.execute(text("DELETE FROM documents"))
        await session.commit()
    yield
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM document_vectors"))
        await session.execute(text("DELETE FROM document_metadata"))
        await session.execute(text("DELETE FROM document_permissions"))
        await session.execute(text("DELETE FROM documents"))
        await session.commit()


async def get_auth_token(client: AsyncClient, username: str = "regular_user") -> str:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "UserPass123!"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_end_to_end_pipeline_success():
    """
    Verify full pipeline execution: upload -> QUEUED -> process -> COMPLETED -> enriched metadata.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Upload Engineering document
        content = (
            b"Software Architecture Specification: AICMS Mini-Project.\n"
            b"The backend is built with FastAPI and PostgreSQL pgvector for vector retrieval.\n"
            b"The pipeline performs text extraction, generates 384-dimensional embeddings, and classifies documents into categories.\n"
            b"Continuous integration and automated testing ensure architectural integrity."
        )
        upload_resp = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("architecture_spec.txt", io.BytesIO(content), "text/plain")},
        )
        assert upload_resp.status_code == 201
        doc_id = upload_resp.json()["document_id"]
        assert upload_resp.json()["status"] == "QUEUED"

        # 2. Trigger synchronous processing pipeline
        process_resp = await client.post(
            f"/api/v1/documents/{doc_id}/process",
            headers=headers,
        )
        assert process_resp.status_code == 200
        assert process_resp.json()["status"] == "COMPLETED"

        # 3. Retrieve enriched metadata
        meta_resp = await client.get(
            f"/api/v1/documents/{doc_id}/metadata",
            headers=headers,
        )
        assert meta_resp.status_code == 200
        meta = meta_resp.json()
        assert meta["document_id"] == doc_id
        assert meta["category_name"] == "Engineering"
        assert meta["category_confidence"] >= 0.50
        assert len(meta["keywords"]) >= 5
        assert len(meta["topics"]) >= 1
        assert meta["embedding_model"] == "sentence-transformers/all-MiniLM-L6-v2"
        assert meta["model_version"] == "v2"
        assert meta["word_count"] > 20


@pytest.mark.asyncio
async def test_pipeline_failure_transitions_to_failed_state():
    """
    Verify that an extraction failure safely sets document status to FAILED
    with a non-empty error message, rather than hanging or failing silently.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_auth_token(client)
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Upload document
        upload_resp = await client.post(
            "/api/v1/documents/upload",
            headers=headers,
            files={"file": ("failing_doc.txt", io.BytesIO(b"Sample failing content"), "text/plain")},
        )
        assert upload_resp.status_code == 201
        doc_id = upload_resp.json()["document_id"]

        # 2. Simulate parser failure
        settings.SIMULATE_PARSER_FAILURE = 1
        try:
            process_resp = await client.post(
                f"/api/v1/documents/{doc_id}/process",
                headers=headers,
            )
            assert process_resp.status_code == 200
            failed_doc = process_resp.json()
            assert failed_doc["status"] == "FAILED"
            assert failed_doc["error_message"] is not None
            assert "parser" in failed_doc["error_message"].lower()

            # Verify status endpoint reflects FAILED
            status_resp = await client.get(
                f"/api/v1/documents/{doc_id}/status",
                headers=headers,
            )
            assert status_resp.status_code == 200
            assert status_resp.json()["status"] == "FAILED"
        finally:
            settings.SIMULATE_PARSER_FAILURE = 0
