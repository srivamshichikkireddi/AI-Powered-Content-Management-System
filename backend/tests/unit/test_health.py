import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch

from backend.app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Verify root status and documentation links."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert "documentation" in data
        assert "health" in data
        assert "X-Correlation-ID" in response.headers
        assert "X-Process-Time" in response.headers


@pytest.mark.asyncio
async def test_health_endpoint():
    """Verify TC-OPS-01 system health check reporting healthy state."""
    transport = ASGITransport(app=app)
    with patch("backend.app.api.health.check_db_health", return_value=True), \
         patch("backend.app.api.health.check_redis_health", return_value=True):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "connected"
            assert data["redis"] == "connected"
            assert "timestamp" in data
            assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_health_degraded_when_service_down():
    """Verify TC-OPS-01 health status degrades when backing services are unreachable."""
    transport = ASGITransport(app=app)
    with patch("backend.app.api.health.check_db_health", return_value=False), \
         patch("backend.app.api.health.check_redis_health", return_value=True):
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "degraded"
            assert data["database"] == "unreachable"
            assert data["redis"] == "connected"


@pytest.mark.asyncio
async def test_standardized_error_format_404():
    """Verify standardized error body {code, message, correlation_id} on 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/non-existent-endpoint")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] == "NOT_FOUND"
        assert "message" in data
        assert "correlation_id" in data
        assert len(data["correlation_id"]) > 0
        assert response.headers["X-Correlation-ID"] == data["correlation_id"]
