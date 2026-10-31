import hashlib
import os
from typing import Tuple
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import settings
from backend.app.core.errors import AICMSException
from backend.app.models.document import Document
from backend.app.models.permission import DocumentPermission
from backend.app.models.user import User
from backend.app.services.audit_service import record_audit_event

SUPPORTED_EXTENSIONS = {"pdf", "docx", "txt"}


def validate_file_signature(content: bytes, ext: str) -> None:
    """
    Validate magic byte content signature against declared extension (AICMS-SR-002, TC-SEC-04).
    Rejects disguised files such as executables or archives renamed to .pdf/.txt.
    """
    if len(content) == 0:
        raise AICMSException(
            code="EMPTY_FILE",
            message="Uploaded file is empty.",
            status_code=400,
        )

    # Executable signatures that should never be permitted
    if content.startswith(b"MZ") or content.startswith(b"\x7fELF"):
        raise AICMSException(
            code="INVALID_FILE_SIGNATURE",
            message="Disguised executable binary detected and rejected.",
            status_code=400,
        )

    if ext == "pdf":
        if not content.startswith(b"%PDF-"):
            raise AICMSException(
                code="INVALID_FILE_SIGNATURE",
                message="File does not have a valid PDF signature header (%PDF-).",
                status_code=400,
            )
    elif ext == "docx":
        # DOCX is an OpenXML Zip package, starts with PK\x03\x04
        if not content.startswith(b"PK\x03\x04"):
            raise AICMSException(
                code="INVALID_FILE_SIGNATURE",
                message="File does not have a valid DOCX OpenXML Zip signature (PK).",
                status_code=400,
            )
    elif ext == "txt":
        # Plain text must not contain binary null bytes or zip headers
        if content.startswith(b"PK\x03\x04") or b"\x00" in content[:1024]:
            raise AICMSException(
                code="INVALID_FILE_SIGNATURE",
                message="File content contains binary signatures incompatible with plain text.",
                status_code=400,
            )
        try:
            content.decode("utf-8")
        except UnicodeDecodeError:
            raise AICMSException(
                code="INVALID_FILE_SIGNATURE",
                message="Plain text file must be valid UTF-8/ASCII encoded.",
                status_code=400,
            )


async def ingest_document(
    db: AsyncSession,
    file: UploadFile,
    user: User,
) -> Document:
    """
    Validate and ingest document: format check, signature check, size limit,
    SHA-256 deduplication (409), disk storage, and state tracking (QUEUED).
    Satisfies AICMS-F-001, F-002, F-003, F-004, SR-002, SR-004.
    """
    filename = file.filename or "unknown"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    # 1. Format validation (AICMS-F-001, TC-UP-04)
    if ext not in SUPPORTED_EXTENSIONS:
        raise AICMSException(
            code="UNSUPPORTED_FORMAT",
            message=f"Unsupported format '.{ext}'. Supported formats are: PDF, DOCX, TXT.",
            status_code=400,
        )

    # Read content
    content = await file.read()
    file_size = len(content)

    # 2. Size limit validation (AICMS-F-002, TC-UP-02)
    if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
        raise AICMSException(
            code="FILE_TOO_LARGE",
            message=f"File size ({file_size / (1024 * 1024):.2f} MB) exceeds maximum allowed limit of 20MB.",
            status_code=413,  # 413 Payload Too Large
        )

    # 3. Magic bytes / signature validation (AICMS-SR-002, TC-SEC-04)
    validate_file_signature(content, ext)

    # 4. SHA-256 duplicate detection (AICMS-SR-004, TC-UP-03)
    sha256_hash = hashlib.sha256(content).hexdigest()
    stmt = select(Document).where(Document.file_hash == sha256_hash)
    result = await db.execute(stmt)
    existing_doc = result.scalar_one_or_none()

    if existing_doc:
        await record_audit_event(
            db,
            event_type="DUPLICATE_UPLOAD_REJECTED",
            status="FAILURE",
            username=user.username,
            user_id=user.id,
            details=f"Duplicate SHA-256 rejected ({sha256_hash}) matching existing doc id={existing_doc.id}",
        )
        raise AICMSException(
            code="DUPLICATE_DOCUMENT",
            message=f"Duplicate document detected. Identical file already exists (id: {existing_doc.id}, hash: {sha256_hash}).",
            status_code=409,  # 409 Conflict per SAD §4.3
        )

    # 5. Persist to storage directory
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)
    stored_filename = f"{sha256_hash}.{ext}"
    storage_path = os.path.join(settings.STORAGE_DIR, stored_filename)

    with open(storage_path, "wb") as f:
        f.write(content)

    # Title defaults to base filename without extension
    title = filename.rsplit(".", 1)[0]

    # 6. Record document in database (Status: QUEUED)
    doc = Document(
        title=title,
        original_filename=filename,
        file_type=ext,
        file_size=file_size,
        file_hash=sha256_hash,
        storage_path=storage_path,
        status="QUEUED",
        owner_id=user.id,
    )
    db.add(doc)
    await db.flush()

    # Assign owner full permissions (ADR-005)
    owner_perm = DocumentPermission(
        document_id=doc.id,
        user_id=user.id,
        can_read=True,
        can_edit=True,
        can_delete=True,
    )
    db.add(owner_perm)

    await record_audit_event(
        db,
        event_type="DOCUMENT_UPLOADED",
        status="SUCCESS",
        username=user.username,
        user_id=user.id,
        details=f"Document ingested: id={doc.id}, file={filename}, size={file_size}B, hash={sha256_hash}",
    )

    await db.commit()
    await db.refresh(doc)
    return doc
