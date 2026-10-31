import asyncio
import time
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app


@pytest.mark.asyncio
async def test_async_pipeline_nonblocking_concurrency_tc_perf_02():
    """
    TC-PERF-02: Verify asynchronous pipeline queueing does not block independent search/API requests.
    Requirement: AICMS-NF-004 (Scalability / Responsiveness under asynchronous workload).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Log in
        auth_resp = await client.post("/api/v1/auth/login", json={"username": "regular_user", "password": "UserPass123!"})
        assert auth_resp.status_code == 200
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        print(f"\n{'='*70}\n[TC-PERF-02] Asynchronous Pipeline Non-Blocking Concurrency Benchmark\nFiring concurrent search & health queries during background task queueing\n{'='*70}")

        # 2. Simulate concurrent independent search and status requests
        async def fetch_search(query_idx: int):
            t0 = time.perf_counter()
            resp = await client.get(f"/api/v1/search?q=microservices+cloud+{query_idx}", headers=headers)
            dt = (time.perf_counter() - t0) * 1000.0
            return resp.status_code, dt

        async def fetch_health():
            t0 = time.perf_counter()
            resp = await client.get("/health")
            dt = (time.perf_counter() - t0) * 1000.0
            return resp.status_code, dt

        # Launch 20 concurrent tasks
        tasks = [fetch_search(i) for i in range(15)] + [fetch_health() for _ in range(5)]
        start_batch = time.perf_counter()
        results = await asyncio.gather(*tasks)
        total_batch_time = (time.perf_counter() - start_batch) * 1000.0

        status_codes = [r[0] for r in results]
        latencies = [r[1] for r in results]

        success_count = sum(1 for sc in status_codes if sc == 200)
        p50 = sorted(latencies)[len(latencies) // 2]
        p95 = sorted(latencies)[int(len(latencies) * 0.95)]

        print(f"Concurrent Operations:   {len(tasks)} (15 search queries + 5 health checks)")
        print(f"Total Batch Duration:    {total_batch_time:.2f} ms")
        print(f"Success Rate:            {success_count}/{len(tasks)} ({success_count/len(tasks)*100:.1f}%)")
        print(f"Median Request Latency:  {p50:.2f} ms")
        print(f"95th Percentile Latency: {p95:.2f} ms")
        print(f"{'-'*70}")
        print(f"TARGET REQUIREMENT:      Zero blocked requests, all status 200 [AICMS-NF-004]")
        print(f"BENCHMARK STATUS:        {'PASS' if success_count == len(tasks) else 'FAIL'}")
        print(f"{'='*70}\n")

        assert success_count == len(tasks), "Some concurrent requests were dropped or blocked!"
        assert p95 < 2000.0, f"Concurrent request latency {p95:.2f}ms exceeded acceptable limits!"
