import json
import re
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.document import Document
from backend.app.models.metadata import DocumentMetadata, DocumentVector
from backend.app.models.permission import DocumentPermission
from backend.app.models.user import User
from backend.app.schemas.search import SearchResultItem, SearchResultResponse
from backend.app.services.ai_service import generate_embedding


def extract_context_snippet(text: str, query: str, max_chars: int = 200) -> str:
    """Extract a contextual snippet around query terms, or the opening sentence."""
    if not text:
        return ""

    clean_text = " ".join(text.split())
    if len(clean_text) <= max_chars:
        return clean_text

    query_terms = [re.escape(w.lower()) for w in re.findall(r"\w+", query) if len(w) > 2]
    if query_terms:
        pattern = re.compile(r"(" + "|".join(query_terms) + r")", re.IGNORECASE)
        match = pattern.search(clean_text)
        if match:
            start_pos = max(0, match.start() - 60)
            end_pos = min(len(clean_text), start_pos + max_chars)
            snippet = clean_text[start_pos:end_pos].strip()
            prefix = "..." if start_pos > 0 else ""
            suffix = "..." if end_pos < len(clean_text) else ""
            return f"{prefix}{snippet}{suffix}"

    return clean_text[:max_chars].strip() + "..."


async def search_documents_semantic(
    db: AsyncSession,
    query: str,
    user: User,
    category: Optional[str] = None,
    file_type: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
) -> SearchResultResponse:
    """
    Execute semantic natural-language search with pgvector cosine distance and
    strict authorization-before-disclosure filtering (AICMS-F-011..015, SR-005, ADR-002).
    """
    trimmed_query = query.strip()
    if not trimmed_query:
        # Graceful empty query state (TC-SR-03)
        return SearchResultResponse(query=query, total=0, limit=limit, offset=offset, results=[])

    # Step 1: Embed query into 384-dimensional dense representation
    query_vec = generate_embedding(trimmed_query)

    # Step 2: Build authorized base query (ADR-002 / TC-SEC-05)
    # User can only search documents they own or have read permission for
    distance_expr = DocumentVector.embedding.cosine_distance(query_vec)

    stmt = (
        select(
            Document,
            DocumentMetadata,
            distance_expr.label("distance"),
        )
        .join(DocumentMetadata, DocumentMetadata.document_id == Document.id)
        .join(DocumentVector, DocumentVector.document_id == Document.id)
        .where(Document.status == "COMPLETED")
    )

    if user.role != "admin":
        stmt = stmt.outerjoin(
            DocumentPermission,
            (DocumentPermission.document_id == Document.id) & (DocumentPermission.user_id == user.id),
        ).where(
            or_(
                Document.owner_id == user.id,
                (DocumentPermission.user_id == user.id) & (DocumentPermission.can_read == True),  # noqa: E712
            )
        )

    # Step 3: Apply search filters (TC-SR-02)
    if category:
        stmt = stmt.where(DocumentMetadata.category_name == category)
    if file_type:
        stmt = stmt.where(Document.file_type == file_type.lower())

    # Step 4: Count total matching accessible documents for pagination (TC-SR-04)
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_count = (await db.execute(count_stmt)).scalar() or 0

    if total_count == 0:
        return SearchResultResponse(
            query=trimmed_query,
            total=0,
            limit=limit,
            offset=offset,
            results=[],
        )

    # Step 5: Rank by cosine distance ascending (closest first) with pagination
    stmt = stmt.order_by(distance_expr.asc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    rows = result.all()

    items: List[SearchResultItem] = []
    for doc, meta, distance in rows:
        # Convert cosine distance d in [0, 2] to similarity score [0.0, 1.0]
        similarity = max(0.0, min(1.0, 1.0 - float(distance)))

        # Extract snippet from extracted_text
        snippet = extract_context_snippet(meta.extracted_text, trimmed_query)
        keywords_list = json.loads(meta.keywords) if meta.keywords else []

        items.append(
            SearchResultItem(
                document_id=doc.id,
                title=doc.title,
                file_type=doc.file_type,
                category_name=meta.category_name,
                similarity_score=round(similarity, 4),
                snippet=snippet,
                keywords=keywords_list,
            )
        )

    return SearchResultResponse(
        query=trimmed_query,
        total=total_count,
        limit=limit,
        offset=offset,
        results=items,
    )
