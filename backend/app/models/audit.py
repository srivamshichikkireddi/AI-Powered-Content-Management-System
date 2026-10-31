from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    username = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=True)
    correlation_id = Column(String(36), nullable=True, index=True)
    status = Column(String(20), nullable=False)  # 'SUCCESS', 'FAILURE'
    details = Column(Text, nullable=True)  # JSON or text description, sanitized

    user = relationship("User", back_populates="audit_logs")
