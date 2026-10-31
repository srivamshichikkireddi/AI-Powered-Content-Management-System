from datetime import datetime
from typing import Optional
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
