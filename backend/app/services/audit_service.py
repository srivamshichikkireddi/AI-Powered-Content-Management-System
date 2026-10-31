import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from backend.app.core.logging import get_correlation_id
from backend.app.models.audit import AuditLog

logger = logging.getLogger(__name__)


async def record_audit_event(
    db: AsyncSession,
    event_type: str,
    status: str,
    username: Optional[str] = None,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    correlation_id: Optional[str] = None,
    details: Optional[str] = None,
) -> AuditLog:
    """
    Log security and lifecycle events to database audit log (satisfies AICMS-SR-001).
    Ensures correlation ID tracing and no raw secrets or tokens in details.
    """
    cid = correlation_id or get_correlation_id()
    audit_entry = AuditLog(
        event_type=event_type,
        status=status,
        username=username,
        user_id=user_id,
        ip_address=ip_address,
        correlation_id=cid,
        details=details,
    )
    db.add(audit_entry)
    await db.commit()
    await db.refresh(audit_entry)

    logger.info(
        f"AUDIT_EVENT: [{event_type}] status={status} user={username} cid={cid}"
    )
    return audit_entry


async def get_audit_logs(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    event_type: Optional[str] = None,
) -> list[AuditLog]:
    """Retrieve audit logs ordered by newest first (auditor / admin access)."""
    stmt = select(AuditLog).order_by(desc(AuditLog.timestamp))
    if event_type:
        stmt = stmt.where(AuditLog.event_type == event_type)
    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())
