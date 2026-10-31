import json
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, File, Query, UploadFile, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_current_user
from backend.app.core.database import AsyncSessionLocal, get_db
from backend.app.core.errors import AICMSException
from backend.app.models.document import Document
from backend.app.models.metadata import DocumentMetadata
from backend.app.models.permission import DocumentPermission
from backend.app.models.user import User
from backend.app.schemas.document import (
    DocumentMetadataResponse,
    DocumentResponse,
    DocumentStatusResponse,
    DocumentUploadResponse,
)
from backend.app.services.pipeline_service import process_document_pipeline
from backend.app.services.storage_service import ingest_document

router = APIRouter(prefix="/documents", tags=["Document Intake & Management"])


async def run_pipeline_task(doc_id: int):
    """Background task runner executing pipeline in its own DB session."""
    async with AsyncSessionLocal() as session:
        try:
            await process_document_pipeline(session, doc_id)
        except Exception:
            pass


async def get_authorized_document(
    db: AsyncSession,
    document_id: int,
    user: User,
    require_action: str = "read",
) -> Document:
    """
    Enforce document-level access control before disclosing metadata or existence (ADR-002, ADR-005).
    Unauthorized access returns 404 to avoid leaking document existence.
    """
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()

    if not doc:
        raise AICMSException(code="NOT_FOUND", message="Document not found", status_code=404)

    # Admin always has full visibility
    if user.role == "admin" or doc.owner_id == user.id:
        return doc

    # Check permission table
    perm_stmt = select(DocumentPermission).where(
        DocumentPermission.document_id == document_id,
        DocumentPermission.user_id == user.id,
    )
    perm_result = await db.execute(perm_stmt)
    perm = perm_result.scalar_one_or_none()

    if not perm:
        raise AICMSException(code="NOT_FOUND", message="Document not found", status_code=404)

    if require_action == "read" and not perm.can_read:
        raise AICMSException(code="NOT_FOUND", message="Document not found", status_code=404)
    if require_action == "edit" and not perm.can_edit:
        raise AICMSException(code="FORBIDDEN", message="Edit permission denied", status_code=403)
    if require_action == "delete" and not perm.can_delete:
        raise AICMSException(code="FORBIDDEN", message="Delete permission denied", status_code=403)

    return doc


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentUploadResponse:
    """
    Ingest and validate document (PDF/DOCX/TXT <= 20MB, magic bytes signature, SHA-256 deduplication).
    Satisfies AICMS-F-001, F-002, F-003, F-004, SR-002, SR-004, TC-UP-01..04, TC-SEC-04.
    """
    doc = await ingest_document(db=db, file=file, user=current_user)
    # Queue asynchronous processing pipeline
    background_tasks.add_task(run_pipeline_task, doc.id)

    return DocumentUploadResponse(
        document_id=doc.id,
        title=doc.title,
        original_filename=doc.original_filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        file_hash=doc.file_hash,
        status=doc.status,
    )


@router.post("/{document_id}/process", response_model=DocumentResponse)
async def trigger_document_processing(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    """
    Explicitly trigger synchronous pipeline processing for testing and evaluation (M4).
    """
    doc = await get_authorized_document(db, document_id, current_user, require_action="edit")
    processed_doc = await process_document_pipeline(db, doc.id)
    return DocumentResponse.model_validate(processed_doc)


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
async def get_document_status(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentStatusResponse:
    """
    Retrieve document processing lifecycle status (QUEUED, PROCESSING, COMPLETED, FAILED).
    """
    doc = await get_authorized_document(db, document_id, current_user, require_action="read")
    return DocumentStatusResponse(
        id=doc.id,
        title=doc.title,
        status=doc.status,
        error_message=doc.error_message,
        updated_at=doc.updated_at,
    )


@router.get("/{document_id}/metadata", response_model=DocumentMetadataResponse)
async def get_document_metadata(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentMetadataResponse:
    """
    Retrieve extracted content, native metadata, category, and AI keywords/topics (AICMS-F-005, F-006, F-008, F-009, F-010).
    """
    doc = await get_authorized_document(db, document_id, current_user, require_action="read")
    stmt = select(DocumentMetadata).where(DocumentMetadata.document_id == doc.id)
    result = await db.execute(stmt)
    meta = result.scalar_one_or_none()

    if not meta:
        raise AICMSException(code="NOT_FOUND", message="Metadata not found or not yet processed.", status_code=404)

    keywords_list = json.loads(meta.keywords) if meta.keywords else []
    topics_list = json.loads(meta.topics) if meta.topics else []

    return DocumentMetadataResponse(
        document_id=doc.id,
        title=doc.title,
        extracted_title=meta.extracted_title,
        extracted_author=meta.extracted_author,
        extracted_date=meta.extracted_date,
        extracted_text=meta.extracted_text,
        word_count=meta.word_count,
        character_count=meta.character_count,
        category_name=meta.category_name,
        category_confidence=meta.category_confidence,
        keywords=keywords_list,
        topics=topics_list,
        embedding_model=meta.embedding_model,
        model_version=meta.model_version,
        revision=meta.revision,
        updated_at=meta.updated_at,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    """
    Retrieve document record by ID with authorization check (404 if unauthorized).
    """
    doc = await get_authorized_document(db, document_id, current_user, require_action="read")
    return DocumentResponse.model_validate(doc)


@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    file_type: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[DocumentResponse]:
    """
    List documents that the current user owns or has read access to.
    """
    if current_user.role == "admin":
        stmt = select(Document)
    else:
        stmt = (
            select(Document)
            .outerjoin(DocumentPermission, DocumentPermission.document_id == Document.id)
            .where(
                or_(
                    Document.owner_id == current_user.id,
                    (DocumentPermission.user_id == current_user.id) & (DocumentPermission.can_read == True),  # noqa: E712
                )
            )
            .distinct()
        )

    if file_type:
        stmt = stmt.where(Document.file_type == file_type.lower())
    if status_filter:
        stmt = stmt.where(Document.status == status_filter.upper())

    stmt = stmt.order_by(Document.id.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    docs = result.scalars().all()
    return [DocumentResponse.model_validate(d) for d in docs]
