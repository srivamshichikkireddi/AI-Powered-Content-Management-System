from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # 'pdf', 'docx', 'txt'
    file_size = Column(Integer, nullable=False)
    file_hash = Column(String(64), unique=True, index=True, nullable=False)  # SHA-256
    storage_path = Column(String(500), nullable=False)
    status = Column(String(20), nullable=False, default="QUEUED", index=True)  # QUEUED, PROCESSING, COMPLETED, FAILED
    error_message = Column(String(500), nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    owner = relationship("User", backref="documents")
    permissions = relationship("DocumentPermission", back_populates="document", cascade="all, delete-orphan")
