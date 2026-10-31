import json
import logging
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.errors import AICMSException
from backend.app.models.category import Category
from backend.app.models.document import Document
from backend.app.models.metadata import DocumentMetadata, DocumentVector
from backend.app.services.ai_service import classify_category, extract_keywords_and_topics, generate_embedding
from backend.app.services.audit_service import record_audit_event
from backend.app.services.extractor import extract_document_content

logger = logging.getLogger(__name__)


async def get_or_create_category(db: AsyncSession, name: str) -> Category:
    """Retrieve or insert category from taxonomy."""
    stmt = select(Category).where(Category.name == name)
    result = await db.execute(stmt)
    cat = result.scalar_one_or_none()
    if not cat:
        cat = Category(name=name, description=f"{name} documents")
        db.add(cat)
        await db.flush()
    return cat


async def process_document_pipeline(db: AsyncSession, document_id: int) -> Document:
    """
    Execute end-to-end extraction and AI enrichment pipeline (M4 / US-03 / US-04).
    1. Parse text & native metadata (PDF, DOCX, TXT)
    2. Compute 384-dim semantic embeddings (all-MiniLM-L6-v2)
    3. Categorize document with confidence score
    4. Extract 5-10 keywords and topic summary
    5. Update status QUEUED -> PROCESSING -> COMPLETED (or FAILED)
    """
    stmt = select(Document).where(Document.id == document_id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()

    if not doc:
        raise AICMSException(code="NOT_FOUND", message="Document not found for pipeline processing.", status_code=404)

    # Transition status: PROCESSING
    doc.status = "PROCESSING"
    await db.commit()

    try:
        # Step 1: Text & Metadata Extraction (AICMS-F-005, F-006, TC-EXT-01/02)
        extracted = extract_document_content(doc.storage_path, doc.file_type)

        text_to_analyze = extracted.text or doc.title

        # Step 2: AI Semantic Embeddings (AICMS-F-008, TC-AI-01)
        embedding_vec = generate_embedding(text_to_analyze)

        # Step 3: Taxonomy Categorization (AICMS-F-009, TC-AI-02)
        category_name, confidence = classify_category(text_to_analyze)
        cat_record = await get_or_create_category(db, category_name)

        # Step 4: Keywords & Topics (AICMS-F-010, TC-AI-03)
        keywords, topics = extract_keywords_and_topics(text_to_analyze)

        # Persist DocumentMetadata
        meta_stmt = select(DocumentMetadata).where(DocumentMetadata.document_id == doc.id)
        meta_res = await db.execute(meta_stmt)
        meta = meta_res.scalar_one_or_none()

        if not meta:
            meta = DocumentMetadata(document_id=doc.id, extracted_text=extracted.text)
            db.add(meta)

        meta.extracted_title = extracted.title
        meta.extracted_author = extracted.author
        meta.extracted_date = extracted.date
        meta.extracted_text = extracted.text
        meta.word_count = extracted.word_count
        meta.character_count = extracted.character_count
        meta.category_id = cat_record.id
        meta.category_name = category_name
        meta.category_confidence = confidence
        meta.keywords = json.dumps(keywords)
        meta.topics = json.dumps(topics)
        meta.embedding_model = "sentence-transformers/all-MiniLM-L6-v2"
        meta.model_version = "v2"

        # Persist DocumentVector (chunk_index 0 for primary document representation)
        vec_stmt = select(DocumentVector).where(DocumentVector.document_id == doc.id)
        vec_res = await db.execute(vec_stmt)
        vector_record = vec_res.scalar_one_or_none()

        if not vector_record:
            vector_record = DocumentVector(
                document_id=doc.id,
                chunk_index=0,
                chunk_text=text_to_analyze[:2000],
                embedding=embedding_vec,
            )
            db.add(vector_record)
        else:
            vector_record.embedding = embedding_vec
            vector_record.chunk_text = text_to_analyze[:2000]

        # Final status
        doc.status = "COMPLETED"
        doc.error_message = None

        await record_audit_event(
            db,
            event_type="DOCUMENT_PROCESSING_COMPLETED",
            status="SUCCESS",
            user_id=doc.owner_id,
            details=f"Processing finished: id={doc.id}, category={category_name} ({confidence:.2f}), {len(keywords)} keywords",
        )

        await db.commit()
        await db.refresh(doc)
        return doc

    except Exception as e:
        logger.error(f"Pipeline processing failed for doc {doc.id}: {e}")
        doc.status = "FAILED"
        doc.error_message = str(e)[:500]

        await record_audit_event(
            db,
            event_type="DOCUMENT_PROCESSING_FAILED",
            status="FAILURE",
            user_id=doc.owner_id,
            details=f"Pipeline error: {str(e)[:250]}",
        )

        await db.commit()
        await db.refresh(doc)
        return doc
