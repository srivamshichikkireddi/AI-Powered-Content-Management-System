from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Taxonomy category name")
    description: Optional[str] = Field(None, max_length=255, description="Category description")


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    document_count: Optional[int] = 0

    class Config:
        from_attributes = True


class ReindexRequest(BaseModel):
    category_name: Optional[str] = Field(None, description="Optional category filter for re-indexing")
    force: bool = Field(False, description="Force re-generation of all dense embeddings")


class ReindexResponse(BaseModel):
    job_id: str
    status: str
    documents_queued: int
    message: str
