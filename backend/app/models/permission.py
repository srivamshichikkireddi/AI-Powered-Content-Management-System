from sqlalchemy import Boolean, Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from backend.app.core.database import Base


class DocumentPermission(Base):
    __tablename__ = "document_permissions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    can_read = Column(Boolean, default=True, nullable=False)
    can_edit = Column(Boolean, default=False, nullable=False)
    can_delete = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint("document_id", "user_id", name="uq_doc_user_permission"),
    )

    document = relationship("Document", back_populates="permissions")
    user = relationship("User", backref="document_permissions")
