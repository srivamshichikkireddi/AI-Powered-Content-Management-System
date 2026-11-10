from typing import List, Optional
from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    document_id: int
    title: str
    file_type: str
    category_name: Optional[str] = None
    similarity_score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
    snippet: str = Field(..., description="Relevant context snippet extracted from document content")
    keywords: List[str] = []


class SearchResultResponse(BaseModel):
    query: str
    total: int
    limit: int
    offset: int
    results: List[SearchResultItem]
