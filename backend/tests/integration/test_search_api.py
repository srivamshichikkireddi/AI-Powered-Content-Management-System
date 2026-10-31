import json
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from backend.app.core.database import AsyncSessionLocal, Base, engine
from backend.app.main import app
from backend.app.models.category import Category
from backend.app.models.document import Document
from backend.app.models.metadata import DocumentMetadata, DocumentVector
from backend.app.models.permission import DocumentPermission
from backend.app.models.user import User
from backend.app.services.ai_service import generate_embedding
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
async def seed_search_test_documents():
    """Seed distinct documents across categories and permissions for search tests."""
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM document_vectors"))
        await session.execute(text("DELETE FROM document_metadata"))
        await session.execute(text("DELETE FROM document_permissions"))
        await session.execute(text("DELETE FROM documents"))
        await session.commit()

        # Retrieve users
        users = {u.username: u for u in (await session.execute(text("SELECT id, username FROM users"))).all()}
        regular_user_id = users["regular_user"].id
        admin_user_id = users["admin_user"].id

        # Retrieve or create categories
        async def get_or_create_category(name: str, desc: str):
            res = await session.execute(text("SELECT id FROM categories WHERE name = :name"), {"name": name})
            row = res.mappings().first()
            if row:
                cat = await session.get(Category, row["id"])
                return cat
            new_cat = Category(name=name, description=desc)
            session.add(new_cat)
            await session.flush()
            return new_cat

        cat_eng = await get_or_create_category("Engineering", "Engineering docs")
        cat_fin = await get_or_create_category("Finance", "Finance docs")
        cat_leg = await get_or_create_category("Legal", "Legal docs")

        # Doc 1: Public Engineering doc owned by regular_user
        doc1 = Document(
            title="FastAPI Microservices Architecture",
            original_filename="fastapi_arch.pdf",
            file_type="pdf",
            file_size=1024,
            file_hash="hash_doc_1_fastapi",
            storage_path="/dummy/fastapi.pdf",
            status="COMPLETED",
            owner_id=regular_user_id,
        )
        # Doc 2: Public Finance doc owned by regular_user
        doc2 = Document(
            title="Quarterly Budget and Revenue Report",
            original_filename="budget_q3.docx",
            file_type="docx",
            file_size=2048,
            file_hash="hash_doc_2_budget",
            storage_path="/dummy/budget.docx",
            status="COMPLETED",
            owner_id=regular_user_id,
        )
        # Doc 3: Private / Restricted Legal doc owned by admin_user (regular_user has NO permission)
        doc3 = Document(
            title="Confidential Acquisition Contract",
            original_filename="secret_acquisition.pdf",
            file_type="pdf",
            file_size=4096,
            file_hash="hash_doc_3_secret",
            storage_path="/dummy/secret.pdf",
            status="COMPLETED",
            owner_id=admin_user_id,
        )
        session.add_all([doc1, doc2, doc3])
        await session.flush()

        # Document Permissions (ADR-005)
        perm1 = DocumentPermission(document_id=doc1.id, user_id=regular_user_id, can_read=True, can_edit=True)
        perm2 = DocumentPermission(document_id=doc2.id, user_id=regular_user_id, can_read=True, can_edit=True)
        perm3 = DocumentPermission(document_id=doc3.id, user_id=admin_user_id, can_read=True, can_edit=True)
        session.add_all([perm1, perm2, perm3])

        # Metadata
        meta1 = DocumentMetadata(
            document_id=doc1.id,
            extracted_title=doc1.title,
            extracted_text="FastAPI asynchronous endpoints provide microservices architecture for vector similarity search and backend services.",
            word_count=15,
            character_count=120,
            category_id=cat_eng.id,
            category_name="Engineering",
            category_confidence=0.95,
            keywords=json.dumps(["fastapi", "microservices", "architecture", "vector", "search"]),
        )
        meta2 = DocumentMetadata(
            document_id=doc2.id,
            extracted_title=doc2.title,
            extracted_text="Fiscal accounting revenue, financial budget statement, quarterly expense balance, and profit margin analysis.",
            word_count=14,
            character_count=110,
            category_id=cat_fin.id,
            category_name="Finance",
            category_confidence=0.92,
            keywords=json.dumps(["revenue", "budget", "financial", "accounting", "profit"]),
        )
        meta3 = DocumentMetadata(
            document_id=doc3.id,
            extracted_title=doc3.title,
            extracted_text="CONFIDENTIAL: Proprietary corporate merger and acquisition contract. Strictly restricted legal compliance terms.",
            word_count=14,
            character_count=115,
            category_id=cat_leg.id,
            category_name="Legal",
            category_confidence=0.98,
            keywords=json.dumps(["confidential", "merger", "acquisition", "contract", "legal"]),
        )
        session.add_all([meta1, meta2, meta3])

        # Vectors (pgvector cosine indexing)
        vec1 = DocumentVector(document_id=doc1.id, chunk_index=0, chunk_text=meta1.extracted_text, embedding=generate_embedding(meta1.extracted_text))
        vec2 = DocumentVector(document_id=doc2.id, chunk_index=0, chunk_text=meta2.extracted_text, embedding=generate_embedding(meta2.extracted_text))
        vec3 = DocumentVector(document_id=doc3.id, chunk_index=0, chunk_text=meta3.extracted_text, embedding=generate_embedding(meta3.extracted_text))
        session.add_all([vec1, vec2, vec3])

        await session.commit()


async def get_auth_token(client: AsyncClient, username: str = "regular_user") -> str:
    pwd = "UserPass123!" if username == "regular_user" else "AdminPass123!"
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": pwd},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_natural_language_semantic_search_ranking_tc_sr_01_and_tc_idx_01():
    """
    TC-SR-01 & TC-IDX-01: Natural language query ranked by cosine similarity using vector index.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_auth_token(client, username="regular_user")
        headers = {"Authorization": f"Bearer {token}"}

        # Query conceptually related to FastAPI microservices
        resp = await client.get(
            "/api/v1/search?q=how do we build python web api microservices",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert len(data["results"]) >= 1

        top_result = data["results"][0]
        assert "FastAPI" in top_result["title"]
        assert top_result["category_name"] == "Engineering"
        assert top_result["similarity_score"] > 0.0
        assert "FastAPI" in top_result["snippet"] or "microservices" in top_result["snippet"]


@pytest.mark.asyncio
async def test_search_filters_category_and_file_type_tc_sr_02():
    """
    TC-SR-02: Search filtering by category and file type.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_auth_token(client, username="regular_user")
        headers = {"Authorization": f"Bearer {token}"}

        # Filter by category=Finance
        resp_cat = await client.get(
            "/api/v1/search?q=report&category=Finance",
            headers=headers,
        )
        assert resp_cat.status_code == 200
        data_cat = resp_cat.json()
        for item in data_cat["results"]:
            assert item["category_name"] == "Finance"

        # Filter by file_type=pdf
        resp_type = await client.get(
            "/api/v1/search?q=report&file_type=pdf",
            headers=headers,
        )
        assert resp_type.status_code == 200
        data_type = resp_type.json()
        for item in data_type["results"]:
            assert item["file_type"] == "pdf"


@pytest.mark.asyncio
async def test_empty_query_and_no_results_state_tc_sr_03():
    """
    TC-SR-03: Empty query and zero-results query handled safely without 500 error.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_auth_token(client, username="regular_user")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Empty query
        resp_empty = await client.get(
            "/api/v1/search?q=",
            headers=headers,
        )
        assert resp_empty.status_code == 200
        data_empty = resp_empty.json()
        assert data_empty["total"] == 0
        assert data_empty["results"] == []

        # 2. Query with non-matching filter (zero results)
        resp_none = await client.get(
            "/api/v1/search?q=budget&category=Operations",
            headers=headers,
        )
        assert resp_none.status_code == 200
        data_none = resp_none.json()
        assert data_none["total"] == 0
        assert data_none["results"] == []


@pytest.mark.asyncio
async def test_search_pagination_tc_sr_04():
    """
    TC-SR-04: Search pagination with limit and offset.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        token = await get_auth_token(client, username="regular_user")
        headers = {"Authorization": f"Bearer {token}"}

        # Page 1: limit=1, offset=0
        resp_p1 = await client.get(
            "/api/v1/search?q=report&limit=1&offset=0",
            headers=headers,
        )
        assert resp_p1.status_code == 200
        data_p1 = resp_p1.json()
        assert data_p1["limit"] == 1
        assert data_p1["offset"] == 0
        assert len(data_p1["results"]) == 1

        # Page 2: limit=1, offset=1
        resp_p2 = await client.get(
            "/api/v1/search?q=report&limit=1&offset=1",
            headers=headers,
        )
        assert resp_p2.status_code == 200
        data_p2 = resp_p2.json()
        assert data_p2["offset"] == 1
        if data_p1["total"] > 1:
            assert len(data_p2["results"]) == 1
            # Different document on page 2
            assert data_p1["results"][0]["document_id"] != data_p2["results"][0]["document_id"]


@pytest.mark.asyncio
async def test_predisclosure_authorization_filter_tc_sec_05():
    """
    TC-SEC-05 & ADR-002: Pre-disclosure authorization check in search.
    A regular user MUST NOT see results, snippets, or titles for confidential
    documents owned by admin, even if searching for exact keywords like 'acquisition contract'.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Search as regular_user for secret document keywords
        user_token = await get_auth_token(client, username="regular_user")
        user_resp = await client.get(
            "/api/v1/search?q=confidential proprietary corporate merger acquisition contract",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert user_resp.status_code == 200
        user_results = user_resp.json()["results"]

        # Restricted document MUST NOT appear in regular user's results
        for item in user_results:
            assert "Confidential Acquisition Contract" not in item["title"]
            assert "Proprietary corporate merger" not in item["snippet"]

        # 2. Search as admin_user for the exact same query
        admin_token = await get_auth_token(client, username="admin_user")
        admin_resp = await client.get(
            "/api/v1/search?q=confidential proprietary corporate merger acquisition contract",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert admin_resp.status_code == 200
        admin_results = admin_resp.json()["results"]

        # Admin user CAN see the restricted document
        admin_doc_titles = [item["title"] for item in admin_results]
        assert "Confidential Acquisition Contract" in admin_doc_titles
