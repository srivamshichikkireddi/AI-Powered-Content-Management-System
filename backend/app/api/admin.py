import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import require_roles
from backend.app.core.database import get_db
from backend.app.models.document import Document
from backend.app.models.metadata import DocumentMetadata, DocumentVector
from backend.app.models.user import User
from backend.app.schemas.category import ReindexRequest, ReindexResponse
from backend.app.services.ai_service import generate_embedding
from backend.app.services.audit_service import record_audit_event
from backend.app.services.metrics_service import metrics_collector

router = APIRouter(prefix="/admin", tags=["Administration & Operations"])


@router.post("/reindex", response_model=ReindexResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_reindex(
    payload: Optional[ReindexRequest] = None,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_roles("admin")),
) -> ReindexResponse:
    """
    Trigger re-indexing of documents after taxonomy or model configuration changes (AICMS-F-020, TC-ADM-02).
    Admin-only operation with traceable job identifier and audit event.
    """
    job_id = f"reindex-{uuid.uuid4().hex[:12]}"
    cat_filter = payload.category_name if payload else None

    stmt = (
        select(Document, DocumentMetadata)
        .join(DocumentMetadata, DocumentMetadata.document_id == Document.id)
        .where(Document.status == "COMPLETED")
    )
    if cat_filter:
        stmt = stmt.where(DocumentMetadata.category_name == cat_filter)

    result = await db.execute(stmt)
    pairs = result.all()
    count = len(pairs)

    # Re-embed each completed document
    for doc, meta in pairs:
        new_vec = generate_embedding(meta.extracted_text)
        # Fetch or update existing vector
        vec_stmt = select(DocumentVector).where(DocumentVector.document_id == doc.id)
        vec_record = (await db.execute(vec_stmt)).scalar_one_or_none()
        if vec_record:
            vec_record.embedding = new_vec
        else:
            db.add(DocumentVector(document_id=doc.id, chunk_index=0, chunk_text=meta.extracted_text, embedding=new_vec))

    await record_audit_event(
        db,
        event_type="REINDEX_TRIGGERED",
        status="SUCCESS",
        username=admin_user.username,
        user_id=admin_user.id,
        details=f"Re-indexing job {job_id} executed for {count} documents (category={cat_filter or 'ALL'})",
    )
    await db.commit()

    return ReindexResponse(
        job_id=job_id,
        status="COMPLETED",
        documents_queued=count,
        message=f"Successfully re-indexed {count} document(s) with job {job_id}.",
    )


@router.get("/metrics")
async def get_admin_metrics(
    admin_user: User = Depends(require_roles("admin")),
):
    """
    Administrative operational metrics summary without sensitive document content (AICMS-F-022, TC-OPS-02).
    """
    return metrics_collector.get_summary()
