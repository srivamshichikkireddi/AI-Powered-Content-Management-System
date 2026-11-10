from contextlib import asynccontextmanager
import logging
import os
import time
import uuid
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from backend.app.api.admin import router as admin_router
from backend.app.api.audit import router as audit_router
from backend.app.api.auth import router as auth_router
from backend.app.api.categories import router as categories_router
from backend.app.api.documents import router as documents_router
from backend.app.api.health import router as health_router
from backend.app.api.search import router as search_router
from backend.app.api.users import router as users_router
from backend.app.core.config import settings
from backend.app.core.database import AsyncSessionLocal, Base, engine
from backend.app.core.errors import register_error_handlers
from backend.app.core.logging import correlation_id_ctx, setup_logging
from backend.app.services.auth_service import seed_initial_users
from backend.app.services.metrics_service import metrics_collector

# Ensure models are loaded for metadata
import backend.app.models  # noqa: F401

logger = logging.getLogger(__name__)
setup_logging(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure storage directory exists
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)

    # Initialize pgvector extension and create tables
    try:
        async with engine.begin() as conn:
            if "postgresql" in settings.DATABASE_URL:
                try:
                    await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                except Exception as e:
                    logger.warning(f"Could not initialize pgvector extension: {e}")
            await conn.run_sync(Base.metadata.create_all)

        # Seed initial test personas (admin, editor, user, auditor)
        async with AsyncSessionLocal() as session:
            await seed_initial_users(session)
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")

    yield
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for AI-Powered Content Management System (AICMS)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_and_timing_middleware(request: Request, call_next) -> Response:
    cid = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
    token = correlation_id_ctx.set(cid)

    start_time = time.perf_counter()
    status_code = 500
    try:
        response: Response = await call_next(request)
        status_code = response.status_code
    finally:
        correlation_id_ctx.reset(token)

    process_time = time.perf_counter() - start_time
    response.headers["X-Correlation-ID"] = cid
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"

    # Record operational metrics (AICMS-F-022, TC-OPS-02, TC-OPS-03)
    try:
        metrics_collector.record_request(
            method=request.method,
            path=request.url.path,
            status_code=status_code,
            duration_sec=process_time,
        )
    except Exception:
        pass

    return response


# Register global error handlers
register_error_handlers(app)

# Include core routers
app.include_router(health_router, prefix="", tags=["Health"])
app.include_router(health_router, prefix=settings.API_V1_STR, tags=["Health"])
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(documents_router, prefix=settings.API_V1_STR)
app.include_router(categories_router, prefix=settings.API_V1_STR)
app.include_router(search_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)


@app.get("/metrics", tags=["Observability"])
async def prometheus_metrics():
    """
    Expose standard Prometheus metrics format for scraping (AICMS-NF-005, TC-OPS-02, TC-OPS-03).
    """
    return Response(
        content=metrics_collector.to_prometheus_format(),
        media_type="text/plain",
    )


@app.get("/", tags=["Root"])
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "running",
        "documentation": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }
