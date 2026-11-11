from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.search import SearchResultResponse
from backend.app.services.search_service import search_documents_semantic

router = APIRouter(prefix="/search", tags=["Semantic Search"])


@router.get("", response_model=SearchResultResponse)
async def search_documents(
    q: str = Query("", description="Natural language query for semantic vector search"),
    category: Optional[str] = Query(None, description="Filter by category taxonomy"),
    file_type: Optional[str] = Query(None, description="Filter by file type (pdf, docx, txt)"),
    limit: int = Query(10, ge=1, le=50, description="Results per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SearchResultResponse:
    """
    Execute natural-language semantic vector search against document embeddings (AICMS-F-011..015).
    Strictly filters results before disclosure based on user permissions (AICMS-SR-005, ADR-002, TC-SEC-05).
    """
    return await search_documents_semantic(
        db=db,
        query=q,
        user=current_user,
        category=category,
        file_type=file_type,
        limit=limit,
        offset=offset,
    )
