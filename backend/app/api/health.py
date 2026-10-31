from datetime import datetime, timezone
import logging
from fastapi import APIRouter
import redis.asyncio as aioredis

from backend.app.core.config import settings
from backend.app.core.database import check_db_health
from backend.app.schemas.common import HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Health & Monitoring"])


async def check_redis_health() -> bool:
    try:
        r = aioredis.from_url(settings.REDIS_URL, socket_timeout=2.0)
        pong = await r.ping()
        await r.aclose()
        return bool(pong)
    except Exception as e:
        logger.warning(f"Redis health check failed: {e}")
        return False


@router.get("/health", response_model=HealthResponse)
async def get_system_health() -> HealthResponse:
    """
    Service health check endpoint (TC-OPS-01).
    Returns real connectivity status for Database and Redis cache/broker.
    """
    db_ok = await check_db_health()
    redis_ok = await check_redis_health()

    status_str = "healthy" if (db_ok and redis_ok) else "degraded"
    db_status = "connected" if db_ok else "unreachable"
    redis_status = "connected" if redis_ok else "unreachable"

    return HealthResponse(
        status=status_str,
        database=db_status,
        redis=redis_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        version="1.0.0",
        environment=settings.ENVIRONMENT,
    )
