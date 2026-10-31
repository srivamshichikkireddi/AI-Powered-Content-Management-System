from datetime import datetime, timedelta, timezone
import logging
from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.core.config import settings
from backend.app.core.errors import AICMSException
from backend.app.core.security import generate_session_token, get_password_hash, verify_password
from backend.app.models.session import UserSession
from backend.app.models.user import User
from backend.app.services.audit_service import record_audit_event

logger = logging.getLogger(__name__)


async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str,
    ip_address: Optional[str] = None,
) -> Tuple[UserSession, User]:
    """
    Authenticate user credentials against bcrypt hash and manage lockout/session state.
    Satisfies AICMS-F-023, AICMS-SR-007, AICMS-SR-008, TC-SEC-07, TC-SEC-08.
    """
    now = datetime.now(timezone.utc)
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        await record_audit_event(
            db,
            event_type="LOGIN_FAILED",
            status="FAILURE",
            username=username,
            ip_address=ip_address,
            details="User not found",
        )
        raise AICMSException(
            code="INVALID_CREDENTIALS",
            message="Invalid username or password",
            status_code=401,
        )

    # Check if account is currently locked (AICMS-SR-008 / TC-SEC-08)
    if user.locked_until and user.locked_until > now:
        await record_audit_event(
            db,
            event_type="ACCOUNT_LOCKED_ATTEMPT",
            status="FAILURE",
            username=username,
            user_id=user.id,
            ip_address=ip_address,
            details=f"Login attempt while locked until {user.locked_until.isoformat()}",
        )
        raise AICMSException(
            code="ACCOUNT_LOCKED",
            message=f"Account is locked due to {settings.MAX_FAILED_LOGIN_ATTEMPTS} failed attempts. Please try again later.",
            status_code=423,  # 423 Locked
        )

    # Verify password against bcrypt hash
    if not verify_password(password, user.hashed_password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
            user.locked_until = now + timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES)
            await record_audit_event(
                db,
                event_type="ACCOUNT_LOCKED",
                status="FAILURE",
                username=username,
                user_id=user.id,
                ip_address=ip_address,
                details=f"Account locked for {settings.LOCKOUT_DURATION_MINUTES} minutes after {user.failed_login_attempts} failed attempts",
            )
        else:
            await record_audit_event(
                db,
                event_type="LOGIN_FAILED",
                status="FAILURE",
                username=username,
                user_id=user.id,
                ip_address=ip_address,
                details=f"Failed attempt {user.failed_login_attempts}/{settings.MAX_FAILED_LOGIN_ATTEMPTS}",
            )

        await db.commit()
        raise AICMSException(
            code="INVALID_CREDENTIALS",
            message="Invalid username or password",
            status_code=401,
        )

    # Successful login: reset failed attempts and lockout
    user.failed_login_attempts = 0
    user.locked_until = None

    # Create server-side session token with 30-min idle expiration (TC-SEC-09)
    session_token = generate_session_token()
    session = UserSession(
        session_token=session_token,
        user_id=user.id,
        created_at=now,
        last_activity_at=now,
        expires_at=now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        is_revoked=False,
    )
    db.add(session)

    await record_audit_event(
        db,
        event_type="LOGIN_SUCCESS",
        status="SUCCESS",
        username=username,
        user_id=user.id,
        ip_address=ip_address,
        details="Authentication successful, session issued",
    )
    await db.commit()
    await db.refresh(session)

    return session, user


async def validate_session_token(db: AsyncSession, token: str) -> User:
    """
    Validate opaque session token and enforce 30-minute idle expiration (TC-SEC-09).
    """
    now = datetime.now(timezone.utc)
    stmt = (
        select(UserSession)
        .where(UserSession.session_token == token)
        .options(selectinload(UserSession.user))
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session or session.is_revoked:
        raise AICMSException(
            code="INVALID_SESSION",
            message="Session is invalid or has been revoked",
            status_code=401,
        )

    # Enforce 30-minute idle timeout
    idle_delta = now - session.last_activity_at
    if idle_delta > timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES):
        session.is_revoked = True
        await db.commit()
        await record_audit_event(
            db,
            event_type="SESSION_EXPIRED",
            status="FAILURE",
            username=session.user.username if session.user else None,
            user_id=session.user_id,
            details=f"Session expired after {idle_delta.total_seconds() / 60:.1f} minutes of inactivity",
        )
        raise AICMSException(
            code="SESSION_EXPIRED",
            message="Session has expired due to 30 minutes of inactivity",
            status_code=401,
        )

    # Slide activity window
    session.last_activity_at = now
    await db.commit()

    return session.user


async def revoke_session(db: AsyncSession, token: str, user: Optional[User] = None) -> bool:
    """Server-side session invalidation upon logout (TC-SEC-09)."""
    stmt = select(UserSession).where(UserSession.session_token == token)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if session:
        session.is_revoked = True
        await record_audit_event(
            db,
            event_type="LOGOUT",
            status="SUCCESS",
            username=user.username if user else None,
            user_id=user.id if user else session.user_id,
            details="Session successfully revoked on logout",
        )
        await db.commit()
        return True
    return False


async def seed_initial_users(db: AsyncSession) -> None:
    """
    Seed initial system personas for RBAC and test verification (STP §13 / TC-ADM-03).
    """
    personas = [
        ("admin_user", "admin@aicms.local", "AdminPass123!", "admin"),
        ("editor_user", "editor@aicms.local", "EditorPass123!", "editor"),
        ("regular_user", "user@aicms.local", "UserPass123!", "user"),
        ("auditor_user", "auditor@aicms.local", "AuditorPass123!", "auditor"),
    ]

    for username, email, raw_password, role in personas:
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        if not existing:
            hashed = get_password_hash(raw_password)
            user = User(
                username=username,
                email=email,
                hashed_password=hashed,
                role=role,
                is_active=True,
            )
            db.add(user)
            logger.info(f"Seeded user: {username} ({role})")

    await db.commit()
