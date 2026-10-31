from contextlib import asynccontextmanager
import os
import time
import uuid
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from backend.app.api.health import router as health_router
from backend.app.core.config import settings
from backend.app.core.database import engine
from backend.app.core.errors import register_error_handlers
from backend.app.core.logging import correlation_id_ctx, setup_logging

setup_logging(settings.LOG_LEVEL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure storage directory exists
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)

    # Initialize pgvector extension if on Postgres
    if "postgresql" in settings.DATABASE_URL:
        try:
            async with engine.begin() as conn:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        except Exception as e:
            # In test environments or when running non-superuser, log warning
            pass
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
    try:
        response: Response = await call_next(request)
    finally:
        correlation_id_ctx.reset(token)

    process_time = time.perf_counter() - start_time
    response.headers["X-Correlation-ID"] = cid
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response


# Register global error handlers
register_error_handlers(app)

# Include core routers
app.include_router(health_router, prefix="", tags=["Health"])
app.include_router(health_router, prefix=settings.API_V1_STR, tags=["Health"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "running",
        "documentation": "/docs",
        "health": "/health",
    }
