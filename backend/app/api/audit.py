from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import require_roles
from backend.app.core.database import get_db
from backend.app.models.user import User
from backend.app.schemas.audit import AuditLogResponse
from backend.app.services.audit_service import get_audit_logs

router = APIRouter(prefix="/audit", tags=["Audit Log Access (Auditor & Admin Only)"])


@router.get("/logs", response_model=List[AuditLogResponse])
async def read_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    event_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    auditor: User = Depends(require_roles("auditor", "admin")),
) -> List[AuditLogResponse]:
    """
    Retrieve structured security and access audit logs (AICMS-SR-001, TC-ADM-03).
    Restricted to users with 'auditor' or 'admin' roles.
    """
    logs = await get_audit_logs(db, limit=limit, offset=offset, event_type=event_type)
    return [AuditLogResponse.model_validate(log) for log in logs]
