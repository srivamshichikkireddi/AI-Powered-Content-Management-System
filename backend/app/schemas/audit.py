from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime
    event_type: str
    user_id: Optional[int] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    correlation_id: Optional[str] = None
    status: str
    details: Optional[str] = None

    class Config:
        from_attributes = True
