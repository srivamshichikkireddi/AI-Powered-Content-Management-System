import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from backend.app.services.metrics_service import metrics_collector


@pytest.mark.asyncio
async def test_service_availability_calculation_tc_ops_03():
    """
    TC-OPS-03: Evaluate system availability and uptime calculation over operating period.
    Requirement: AICMS-NF-002 (Target >= 99.5% monthly availability excluding approved maintenance).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Admin login
        auth_resp = await client.post("/api/v1/auth/login", json={"username": "admin_user", "password": "AdminPass123!"})
        assert auth_resp.status_code == 200
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        print(f"\n{'='*70}\n[TC-OPS-03] Service Availability & Uptime Evaluation\nEvaluating operational telemetry against AICMS-NF-002 SLA\n{'='*70}")

        # 2. Query admin metrics endpoint
        metrics_resp = await client.get("/api/v1/admin/metrics", headers=headers)
        assert metrics_resp.status_code == 200
        data = metrics_resp.json()

        uptime_sec = data["uptime_seconds"]
        availability_pct = data["availability_percentage"]
        total_requests = data["total_requests"]

        # 3. Simulate expected client 4xx errors (client errors do not count as downtime)
        await client.post("/api/v1/auth/login", json={"username": "unknown", "password": "wrong"})
        await client.get("/api/v1/documents/99999", headers=headers)

        updated_avail = metrics_collector.get_availability_percentage()

        print(f"Service Uptime:          {uptime_sec:.2f} seconds")
        print(f"Total Requests Tracked:  {total_requests}")
        print(f"Calculated Availability: {updated_avail:.2f}%")
        print(f"{'-'*70}")
        print(f"TARGET REQUIREMENT:      Availability >= 99.50% (AICMS-NF-002)")
        print(f"BENCHMARK STATUS:        {'PASS' if updated_avail >= 99.5 else 'FAIL'}")
        print(f"{'='*70}\n")

        assert uptime_sec > 0.0, "Uptime counter was not initialized!"
        assert updated_avail >= 99.5, f"Availability {updated_avail:.2f}% below 99.5% SLA target!"
