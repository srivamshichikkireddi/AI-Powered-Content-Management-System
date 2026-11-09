from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector

from backend.app.core.database import Base


class DocumentMetadata(Base):
    __tablename__ = "document_metadata"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    extracted_title = Column(String(255), nullable=True)
    extracted_author = Column(String(255), nullable=True)
    extracted_date = Column(String(100), nullable=True)
    extracted_text = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=False, default=0)
    character_count = Column(Integer, nullable=False, default=0)

    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    category_name = Column(String(100), nullable=True)
    category_confidence = Column(Float, nullable=True)

    keywords = Column(Text, nullable=True)  # JSON or comma-separated list of keywords
    topics = Column(Text, nullable=True)  # JSON or descriptive topic keywords

    embedding_model = Column(String(100), nullable=True, default="all-MiniLM-L6-v2")
    model_version = Column(String(50), nullable=True, default="v2")
    revision = Column(Integer, nullable=False, default=1)  # Optimistic concurrency revision

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    document = relationship("Document", backref="doc_metadata")
    category = relationship("Category", back_populates="metadata_records")


class DocumentVector(Base):
    __tablename__ = "document_vectors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False, default=0)
    chunk_text = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)  # 384 dimensions matching all-MiniLM-L6-v2
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    document = relationship("Document", backref="vectors")
