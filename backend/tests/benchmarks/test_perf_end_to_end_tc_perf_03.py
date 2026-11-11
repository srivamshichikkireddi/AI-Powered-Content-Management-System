import time
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.core.database import AsyncSessionLocal
from backend.app.main import app
from backend.app.models.metadata import DocumentMetadata, DocumentVector
from backend.app.services.pipeline_service import process_document_pipeline
from backend.tests.benchmarks.benchmark_corpus import TEN_PAGE_SPECIFICATION_TEXT
from sqlalchemy import select


@pytest.mark.asyncio
async def test_ten_page_document_processing_time_tc_perf_03():
    """
    TC-PERF-03: Process a 10-page text-based document end-to-end (intake, extraction,
    categorization, TF-IDF keywords, embedding, and vector indexing).
    Requirement: AICMS-NF-010 (Processing time <= 60 seconds).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Authenticate
        auth_resp = await client.post("/api/v1/auth/login", json={"username": "regular_user", "password": "UserPass123!"})
        assert auth_resp.status_code == 200
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        print(f"\n{'='*70}\n[TC-PERF-03] 10-Page Document End-to-End Processing Benchmark\nEvaluating full intake -> parse -> AI enrichment -> vector indexing\n{'='*70}")

        # Ingest document with unique run nonce for test idempotency
        unique_text = f"RUN_NONCE={time.time_ns()}\n\n" + TEN_PAGE_SPECIFICATION_TEXT
        file_bytes = unique_text.encode("utf-8")
        files = {"file": ("enterprise_platform_spec_10page.txt", file_bytes, "text/plain")}

        t0 = time.perf_counter()

        upload_resp = await client.post("/api/v1/documents/upload", headers=headers, files=files)
        assert upload_resp.status_code == 201
        doc_id = upload_resp.json()["document_id"]

        # Run pipeline
        async with AsyncSessionLocal() as session:
            processed_doc = await process_document_pipeline(session, doc_id)

        total_elapsed_sec = time.perf_counter() - t0

        assert processed_doc.status == "COMPLETED"

        # Verify artifacts
        async with AsyncSessionLocal() as session:
            meta = (await session.execute(select(DocumentMetadata).where(DocumentMetadata.document_id == doc_id))).scalar_one()
            vec = (await session.execute(select(DocumentVector).where(DocumentVector.document_id == doc_id))).scalar_one()

        print(f"Document ID:             {doc_id}")
        print(f"Original Text Length:    {len(file_bytes)} bytes (~10 pages equivalent)")
        print(f"Extracted Word Count:    {meta.word_count} words")
        print(f"Assigned Category:       {meta.category_name} (Confidence: {meta.category_confidence:.2f})")
        print(f"Vector Dimensions:       {len(vec.embedding)} dimensions")
        print(f"Total Processing Time:   {total_elapsed_sec:.4f} seconds ({total_elapsed_sec * 1000.0:.2f} ms)")
        print(f"{'-'*70}")
        print(f"TARGET REQUIREMENT:      <= 60.00 seconds (AICMS-NF-010)")
        print(f"BENCHMARK STATUS:        {'PASS' if total_elapsed_sec <= 60.0 else 'FAIL'}")
        print(f"{'='*70}\n")

        assert total_elapsed_sec <= 60.0, f"Processing time {total_elapsed_sec:.2f}s exceeded 60s limit!"
