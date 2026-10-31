from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    id: int
    title: str
    original_filename: str
    file_type: str
    file_size: int
    file_hash: str
    status: str
    error_message: Optional[str] = None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentStatusResponse(BaseModel):
    id: int
    title: str
    status: str = Field(..., description="QUEUED, PROCESSING, COMPLETED, FAILED")
    error_message: Optional[str] = None
    updated_at: datetime


class DocumentUploadResponse(BaseModel):
    document_id: int
    title: str
    original_filename: str
    file_type: str
    file_size: int
    file_hash: str
    status: str
    message: str = "Document successfully ingested and queued for processing"


class DocumentMetadataResponse(BaseModel):
    document_id: int
    title: str
    extracted_title: Optional[str] = None
    extracted_author: Optional[str] = None
    extracted_date: Optional[str] = None
    extracted_text: str
    word_count: int
    character_count: int
    category_name: Optional[str] = None
    category_confidence: Optional[float] = None
    keywords: List[str] = []
    topics: List[str] = []
    embedding_model: Optional[str] = None
    model_version: Optional[str] = None
    revision: int
    updated_at: datetime
