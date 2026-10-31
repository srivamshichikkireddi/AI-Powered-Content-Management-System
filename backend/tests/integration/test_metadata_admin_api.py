import json
import os
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from backend.app.core.database import AsyncSessionLocal, Base, engine
from backend.app.main import app
from backend.app.models.category import Category
from backend.app.models.document import Document
from backend.app.models.metadata import DocumentMetadata, DocumentVector
from backend.app.models.permission import DocumentPermission
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
async def seed_metadata_test_data():
    """Seed clean state for metadata, taxonomy, deletion and metrics tests."""
    async with AsyncSessionLocal() as session:
        await session.execute(text("DELETE FROM document_vectors"))
        await session.execute(text("DELETE FROM document_metadata"))
        await session.execute(text("DELETE FROM document_permissions"))
        await session.execute(text("DELETE FROM documents"))
        await session.commit()

        # Retrieve users
        users = {u.username: u for u in (await session.execute(text("SELECT id, username FROM users"))).all()}
        regular_user_id = users["regular_user"].id
        editor_user_id = users["editor_user"].id
        admin_user_id = users["admin_user"].id

        # Retrieve or create categories
        async def get_or_create_cat(name: str, desc: str):
            res = await session.execute(text("SELECT id FROM categories WHERE name = :name"), {"name": name})
            row = res.mappings().first()
            if row:
                return await session.get(Category, row["id"])
            new_cat = Category(name=name, description=desc)
            session.add(new_cat)
            await session.flush()
            return new_cat

        cat_eng = await get_or_create_cat("Engineering", "Engineering specs")
        cat_ops = await get_or_create_cat("Operations", "Operations procedures")

        # Create dummy physical file for deletion verification
        dummy_path = "/tmp/test_deletable_doc.pdf"
        os.makedirs("/tmp", exist_ok=True)
        with open(dummy_path, "wb") as f:
            f.write(b"%PDF-1.4 dummy content for deletion test")

        # Seed Document
        doc = Document(
            title="Containerized Infrastructure Deployment",
            original_filename="deployment.pdf",
            file_type="pdf",
            file_size=1024,
            file_hash="hash_m6_test_deployment",
            storage_path=dummy_path,
            status="COMPLETED",
            owner_id=regular_user_id,
        )
        session.add(doc)
        await session.flush()

        # Permissions: regular_user (owner), editor_user (can_read, can_edit)
        perm_owner = DocumentPermission(document_id=doc.id, user_id=regular_user_id, can_read=True, can_edit=True, can_delete=True)
        perm_editor = DocumentPermission(document_id=doc.id, user_id=editor_user_id, can_read=True, can_edit=True, can_delete=False)
        session.add_all([perm_owner, perm_editor])

        # Metadata
        meta = DocumentMetadata(
            document_id=doc.id,
            extracted_title="Containerized Infrastructure Deployment",
            extracted_author="DevOps Team",
            extracted_text="Deploying containerized microservices using docker-compose and Kubernetes orchestration.",
            word_count=10,
            character_count=80,
            category_id=cat_eng.id,
            category_name=cat_eng.name,
            category_confidence=0.91,
            keywords=json.dumps(["docker", "kubernetes", "microservices"]),
            topics=json.dumps(["DevOps", "Infrastructure"]),
            revision=1,
        )
        session.add(meta)
        await session.flush()

        # Vector
        vec = DocumentVector(
            document_id=doc.id,
            chunk_index=0,
            chunk_text=meta.extracted_text,
            embedding=generate_embedding(meta.extracted_text),
        )
        session.add(vec)
        await session.commit()


async def get_token(client: AsyncClient, username: str) -> str:
    pwd_map = {
        "admin_user": "AdminPass123!",
        "editor_user": "EditorPass123!",
        "regular_user": "UserPass123!",
        "auditor_user": "AuditorPass123!",
    }
    resp = await client.post("/api/v1/auth/login", json={"username": username, "password": pwd_map[username]})
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_metadata_correction_and_concurrency_tc_md_01():
    """
    TC-MD-01: Authorized editor modifies category/keywords, optimistic concurrency (409 on conflict),
    non-editor denied (403), audit trail generated (AICMS-F-016, AICMS-SR-006, TC-SEC-02).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        editor_token = await get_token(client, "editor_user")
        user_token = await get_token(client, "regular_user")

        # 1. Non-editor user attempts to update metadata -> 403 Forbidden
        async with AsyncSessionLocal() as session:
            doc = (await session.execute(text("SELECT id FROM documents LIMIT 1"))).scalar_one()

        resp_unauth = await client.patch(
            f"/api/v1/documents/{doc}/metadata",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"category_name": "Operations", "revision": 1},
        )
        assert resp_unauth.status_code == 403
        assert resp_unauth.json()["code"] == "FORBIDDEN_ROLE"

        # 2. Concurrency Conflict: Editor submits with wrong revision number -> 409 Conflict
        resp_conflict = await client.patch(
            f"/api/v1/documents/{doc}/metadata",
            headers={"Authorization": f"Bearer {editor_token}"},
            json={"category_name": "Operations", "revision": 999},  # Wrong revision
        )
        assert resp_conflict.status_code == 409
        assert resp_conflict.json()["code"] == "CONCURRENCY_CONFLICT"

        # 3. Successful update by editor with correct revision (revision=1)
        resp_success = await client.patch(
            f"/api/v1/documents/{doc}/metadata",
            headers={"Authorization": f"Bearer {editor_token}"},
            json={
                "category_name": "Operations",
                "keywords": ["devops", "cloud", "orchestration", "containers"],
                "topics": ["Cloud Architecture"],
                "revision": 1,
            },
        )
        assert resp_success.status_code == 200
        data = resp_success.json()
        assert data["category_name"] == "Operations"
        assert "cloud" in data["keywords"]
        assert data["revision"] == 2  # Revision incremented!

        # 4. Subsequent update using stale revision 1 must now fail with 409
        resp_stale = await client.patch(
            f"/api/v1/documents/{doc}/metadata",
            headers={"Authorization": f"Bearer {editor_token}"},
            json={"category_name": "Operations", "revision": 1},
        )
        assert resp_stale.status_code == 409

        # 5. Verify audit trail recorded event (TC-SEC-02)
        async with AsyncSessionLocal() as session:
            audit = (
                await session.execute(
                    text("SELECT event_type, username FROM audit_logs WHERE event_type = 'METADATA_UPDATED' ORDER BY id DESC LIMIT 1")
                )
            ).mappings().first()
            assert audit is not None
            assert audit["username"] == "editor_user"


@pytest.mark.asyncio
async def test_taxonomy_administration_rbac_and_integrity_tc_adm_01():
    """
    TC-ADM-01: Admin creates and deletes taxonomy categories with referential integrity protection.
    Non-admin attempts are denied with 403. Audited action (AICMS-F-019, AICMS-SR-001, TC-SEC-02).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        admin_token = await get_token(client, "admin_user")
        editor_token = await get_token(client, "editor_user")

        # 1. Non-admin attempts to create category -> 403 Forbidden
        resp_non_admin = await client.post(
            "/api/v1/categories",
            headers={"Authorization": f"Bearer {editor_token}"},
            json={"name": "Cybersecurity", "description": "Security policies"},
        )
        assert resp_non_admin.status_code == 403

        # 2. Admin creates new category -> 201 Created
        resp_create = await client.post(
            "/api/v1/categories",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Cybersecurity", "description": "Security policies"},
        )
        assert resp_create.status_code == 201
        new_cat_id = resp_create.json()["id"]
        assert resp_create.json()["name"] == "Cybersecurity"

        # 3. Duplicate creation rejected -> 409 Conflict
        resp_dup = await client.post(
            "/api/v1/categories",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Cybersecurity", "description": "Duplicate"},
        )
        assert resp_dup.status_code == 409

        # 4. Referential integrity: Admin attempts to delete category assigned to documents -> 409 Conflict
        async with AsyncSessionLocal() as session:
            eng_cat = (await session.execute(text("SELECT id FROM categories WHERE name = 'Engineering'"))).scalar_one()

        resp_del_in_use = await client.delete(
            f"/api/v1/categories/{eng_cat}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp_del_in_use.status_code == 409
        assert resp_del_in_use.json()["code"] == "CATEGORY_IN_USE"

        # 5. Admin successfully deletes unused category -> 200 OK
        resp_del = await client.delete(
            f"/api/v1/categories/{new_cat_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp_del.status_code == 200

        # 6. Verify audit logs recorded both actions
        async with AsyncSessionLocal() as session:
            events = (
                await session.execute(
                    text("SELECT event_type FROM audit_logs WHERE event_type IN ('TAXONOMY_CREATED', 'TAXONOMY_DELETED')")
                )
            ).scalars().all()
            assert "TAXONOMY_CREATED" in events
            assert "TAXONOMY_DELETED" in events


@pytest.mark.asyncio
async def test_admin_reindexing_job_tc_adm_02():
    """
    TC-ADM-02: Admin triggers re-indexing following taxonomy or model configuration update.
    Returns job identifier, completed status, and queues eligible documents (AICMS-F-020).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        admin_token = await get_token(client, "admin_user")
        user_token = await get_token(client, "regular_user")

        # 1. Non-admin denied -> 403 Forbidden
        resp_unauth = await client.post(
            "/api/v1/admin/reindex",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp_unauth.status_code == 403

        # 2. Admin triggers re-index -> 202 Accepted
        resp_reindex = await client.post(
            "/api/v1/admin/reindex",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"force": True},
        )
        assert resp_reindex.status_code == 202
        data = resp_reindex.json()
        assert data["job_id"].startswith("reindex-")
        assert data["status"] == "COMPLETED"
        assert data["documents_queued"] >= 1

        # 3. Verify audit event
        async with AsyncSessionLocal() as session:
            audit = (
                await session.execute(
                    text("SELECT event_type, username FROM audit_logs WHERE event_type = 'REINDEX_TRIGGERED'")
                )
            ).mappings().first()
            assert audit is not None
            assert audit["username"] == "admin_user"


@pytest.mark.asyncio
async def test_document_deletion_and_vector_purge_tc_data_01_and_02():
    """
    TC-DATA-01 & TC-DATA-02: Document deletion purges search index, metadata, vectors,
    permissions, physical storage file, and generates audit log (AICMS-F-021, AICMS-NF-007).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        owner_token = await get_token(client, "regular_user")
        editor_token = await get_token(client, "editor_user")

        async with AsyncSessionLocal() as session:
            doc = (await session.execute(text("SELECT id, storage_path FROM documents LIMIT 1"))).mappings().first()
            doc_id = doc["id"]
            file_path = doc["storage_path"]

        # 1. Editor (non-owner, without delete perm) attempts delete -> 403 Forbidden
        resp_unauth = await client.delete(
            f"/api/v1/documents/{doc_id}",
            headers={"Authorization": f"Bearer {editor_token}"},
        )
        assert resp_unauth.status_code == 403

        # 2. Owner successfully deletes document -> 200 OK
        resp_delete = await client.delete(
            f"/api/v1/documents/{doc_id}",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp_delete.status_code == 200

        # 3. Search query no longer returns the deleted document (TC-DATA-01)
        resp_search = await client.get(
            "/api/v1/search?q=containerized microservices kubernetes",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp_search.status_code == 200
        search_data = resp_search.json()
        doc_ids_in_search = [r["document_id"] for r in search_data["results"]]
        assert doc_id not in doc_ids_in_search

        # 4. Data consistency check (TC-DATA-02): zero orphan records remain
        async with AsyncSessionLocal() as session:
            meta_count = (await session.execute(text("SELECT count(*) FROM document_metadata WHERE document_id = :id"), {"id": doc_id})).scalar()
            vec_count = (await session.execute(text("SELECT count(*) FROM document_vectors WHERE document_id = :id"), {"id": doc_id})).scalar()
            perm_count = (await session.execute(text("SELECT count(*) FROM document_permissions WHERE document_id = :id"), {"id": doc_id})).scalar()
            doc_count = (await session.execute(text("SELECT count(*) FROM documents WHERE id = :id"), {"id": doc_id})).scalar()

            assert meta_count == 0, "Orphan document_metadata records found!"
            assert vec_count == 0, "Orphan document_vectors records found!"
            assert perm_count == 0, "Orphan document_permissions records found!"
            assert doc_count == 0, "Document still exists!"

        # 5. Physical disk file deleted
        assert not os.path.exists(file_path), "Physical file was not removed from storage!"

        # 6. Audit event verified
        async with AsyncSessionLocal() as session:
            audit = (
                await session.execute(
                    text("SELECT event_type, username FROM audit_logs WHERE event_type = 'DOCUMENT_DELETED' ORDER BY id DESC LIMIT 1")
                )
            ).mappings().first()
            assert audit is not None
            assert audit["username"] == "regular_user"


@pytest.mark.asyncio
async def test_operational_metrics_and_availability_tc_ops_02_and_03():
    """
    TC-OPS-02 & TC-OPS-03: Expose operational metrics without document secrets,
    Prometheus /metrics exposition, and availability calculation >= 99.5% (AICMS-F-022, AICMS-NF-002).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        admin_token = await get_token(client, "admin_user")
        user_token = await get_token(client, "regular_user")

        # 1. Non-admin denied on admin metrics endpoint -> 403 Forbidden
        resp_unauth = await client.get(
            "/api/v1/admin/metrics",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp_unauth.status_code == 403

        # 2. Admin inspects metrics summary -> 200 OK
        resp_metrics = await client.get(
            "/api/v1/admin/metrics",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp_metrics.status_code == 200
        metrics = resp_metrics.json()
        assert metrics["uptime_seconds"] >= 0.0
        assert metrics["availability_percentage"] >= 99.5  # Meets AICMS-NF-002 SLA target
        assert "uploads" in metrics
        assert "search" in metrics
        assert metrics["total_requests"] >= 1

        # Verify no raw document content or secrets leaked in metrics
        metrics_str = json.dumps(metrics)
        assert "password" not in metrics_str.lower()
        assert "secret" not in metrics_str.lower()
        assert "token" not in metrics_str.lower()

        # 3. Prometheus scraper endpoint /metrics -> 200 OK text/plain
        resp_prom = await client.get("/metrics")
        assert resp_prom.status_code == 200
        assert "text/plain" in resp_prom.headers.get("content-type", "")
        prom_text = resp_prom.text
        assert "aicms_service_uptime_seconds" in prom_text
        assert "aicms_availability_ratio" in prom_text
        assert "aicms_http_requests_total" in prom_text
