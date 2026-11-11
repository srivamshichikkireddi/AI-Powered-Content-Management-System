from datetime import datetime, timedelta, timezone
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text, select

from backend.app.core.database import AsyncSessionLocal, Base, engine
from backend.app.main import app
from backend.app.models.session import UserSession
from backend.app.models.user import User
from backend.app.services.auth_service import seed_initial_users


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Ensure tables exist and seed initial personas once for session."""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        await seed_initial_users(session)
    yield
    await engine.dispose()


@pytest.fixture(autouse=True)
async def reset_user_lockouts():
    """Ensure regular_user is unlocked before and after each test."""
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.username == "regular_user")
        res = await session.execute(stmt)
        u = res.scalar_one_or_none()
        if u:
            u.failed_login_attempts = 0
            u.locked_until = None
            await session.commit()
    yield
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.username == "regular_user")
        res = await session.execute(stmt)
        u = res.scalar_one_or_none()
        if u:
            u.failed_login_attempts = 0
            u.locked_until = None
            await session.commit()


@pytest.mark.asyncio
async def test_login_success_and_profile():
    """Verify successful authentication issues session token (AICMS-F-023)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login with seeded regular user
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "regular_user", "password": "UserPass123!"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] == 1800
        assert data["user"]["username"] == "regular_user"
        assert data["user"]["role"] == "user"

        token = data["access_token"]

        # 2. Access /auth/me with bearer token
        me_resp = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_resp.status_code == 200
        me_data = me_resp.json()
        assert me_data["username"] == "regular_user"


@pytest.mark.asyncio
async def test_account_lockout_after_5_failed_attempts_tc_sec_08():
    """
    TC-SEC-08: 5 consecutive failed logins lock the account; 6th attempt returns 423.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Attempts 1 to 5: must return 401 INVALID_CREDENTIALS
        for i in range(1, 6):
            resp = await client.post(
                "/api/v1/auth/login",
                json={"username": "regular_user", "password": "WrongPassword999!"},
            )
            assert resp.status_code == 401
            assert resp.json()["code"] == "INVALID_CREDENTIALS"

        # Attempt 6: Account is now locked; must return 423 Locked
        resp_6 = await client.post(
            "/api/v1/auth/login",
            json={"username": "regular_user", "password": "WrongPassword999!"},
        )
        assert resp_6.status_code == 423
        data_6 = resp_6.json()
        assert data_6["code"] == "ACCOUNT_LOCKED"
        assert "locked" in data_6["message"].lower()

        # Even with correct password, attempt while locked is blocked with 423
        resp_locked_valid = await client.post(
            "/api/v1/auth/login",
            json={"username": "regular_user", "password": "UserPass123!"},
        )
        assert resp_locked_valid.status_code == 423
        assert resp_locked_valid.json()["code"] == "ACCOUNT_LOCKED"


@pytest.mark.asyncio
async def test_logout_invalidates_session_tc_sec_09():
    """
    TC-SEC-09: Logout revokes session on server; revoked token returns 401.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "regular_user", "password": "UserPass123!"},
        )
        assert resp.status_code == 200
        token = resp.json()["access_token"]

        # 2. Confirm token works
        resp_me = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp_me.status_code == 200

        # 3. Logout
        resp_logout = await client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp_logout.status_code == 200
        assert resp_logout.json()["status"] == "logged_out"

        # 4. Attempt to use revoked token -> 401 INVALID_SESSION
        resp_revoked = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp_revoked.status_code == 401
        assert resp_revoked.json()["code"] == "INVALID_SESSION"


@pytest.mark.asyncio
async def test_session_idle_timeout_tc_sec_09():
    """
    TC-SEC-09: 30-minute idle inactivity timeout.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "regular_user", "password": "UserPass123!"},
        )
        assert resp.status_code == 200
        token = resp.json()["access_token"]

        # 2. Simulate 31 minutes of idle inactivity
        async with AsyncSessionLocal() as session:
            stmt = select(UserSession).where(UserSession.session_token == token)
            res = await session.execute(stmt)
            db_sess = res.scalar_one_or_none()
            assert db_sess is not None
            db_sess.last_activity_at = datetime.now(timezone.utc) - timedelta(minutes=31)
            await session.commit()

        # 3. Request with idle token -> 401 SESSION_EXPIRED
        resp_expired = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp_expired.status_code == 401
        assert resp_expired.json()["code"] == "SESSION_EXPIRED"


@pytest.mark.asyncio
async def test_role_based_access_control_tc_adm_03():
    """
    TC-ADM-03: Verify RBAC permissions across admin, editor, regular user, and auditor.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Login as regular_user
        user_login = await client.post(
            "/api/v1/auth/login",
            json={"username": "regular_user", "password": "UserPass123!"},
        )
        user_token = user_login.json()["access_token"]

        # 2. Login as admin_user
        admin_login = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin_user", "password": "AdminPass123!"},
        )
        admin_token = admin_login.json()["access_token"]

        # 3. Login as auditor_user
        auditor_login = await client.post(
            "/api/v1/auth/login",
            json={"username": "auditor_user", "password": "AuditorPass123!"},
        )
        auditor_token = auditor_login.json()["access_token"]

        # A. Admin-only endpoint: /api/v1/users
        # Regular user should be forbidden (403)
        user_access_users = await client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert user_access_users.status_code == 403
        assert user_access_users.json()["code"] == "FORBIDDEN_ROLE"

        # Admin user should succeed (200)
        admin_access_users = await client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert admin_access_users.status_code == 200
        users_list = admin_access_users.json()
        assert len(users_list) >= 4

        # B. Auditor endpoint: /api/v1/audit/logs
        # Regular user should be forbidden (403)
        user_access_audit = await client.get(
            "/api/v1/audit/logs",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert user_access_audit.status_code == 403

        # Auditor user should succeed (200)
        auditor_access_audit = await client.get(
            "/api/v1/audit/logs",
            headers={"Authorization": f"Bearer {auditor_token}"},
        )
        assert auditor_access_audit.status_code == 200
        audit_logs = auditor_access_audit.json()
        assert len(audit_logs) > 0
        event_types = [log["event_type"] for log in audit_logs]
        assert "LOGIN_SUCCESS" in event_types
