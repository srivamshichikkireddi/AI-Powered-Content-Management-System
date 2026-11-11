import time
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from backend.app.scripts.seed_demo import seed_demo
from backend.tests.benchmarks.benchmark_corpus import SEARCH_BENCHMARK_QUERIES


@pytest.mark.asyncio
async def test_search_latency_p90_benchmark_tc_perf_01():
    """
    TC-PERF-01: Natural language search load latency benchmarking.
    Requirement: AICMS-NF-001 (90% of search requests return results within 3 seconds: p90 <= 3.0s).
    """
    # Ensure seed documents are populated
    await seed_demo()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Authenticate
        auth_resp = await client.post("/api/v1/auth/login", json={"username": "regular_user", "password": "UserPass123!"})
        assert auth_resp.status_code == 200
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Run 50 search requests (repeat benchmark query set 2.5 times)
        queries = (SEARCH_BENCHMARK_QUERIES * 3)[:50]
        latencies_ms = []

        print(f"\n{'='*70}\n[TC-PERF-01] Search Latency & Performance Benchmark\nExecuting 50 search requests against vector engine\n{'='*70}")

        for i, q_item in enumerate(queries):
            start = time.perf_counter()
            resp = await client.get(f"/api/v1/search?q={urllib_parse(q_item['query'])}", headers=headers)
            elapsed = (time.perf_counter() - start) * 1000.0
            latencies_ms.append(elapsed)
            assert resp.status_code == 200

        latencies_sorted = sorted(latencies_ms)
        min_lat = latencies_sorted[0]
        max_lat = latencies_sorted[-1]
        mean_lat = sum(latencies_sorted) / len(latencies_sorted)
        p50 = latencies_sorted[int(len(latencies_sorted) * 0.50)]
        p90 = latencies_sorted[int(len(latencies_sorted) * 0.90)]
        p99 = latencies_sorted[int(len(latencies_sorted) * 0.99)]

        print(f"Total Requests Executed: {len(latencies_ms)}")
        print(f"Minimum Latency:         {min_lat:.2f} ms")
        print(f"Mean Latency:            {mean_lat:.2f} ms")
        print(f"Median (p50) Latency:    {p50:.2f} ms")
        print(f"90th Percentile (p90):   {p90:.2f} ms ({p90/1000.0:.4f} s)")
        print(f"99th Percentile (p99):   {p99:.2f} ms")
        print(f"Maximum Latency:         {max_lat:.2f} ms")
        print(f"{'-'*70}")
        print(f"TARGET REQUIREMENT:      p90 <= 3000 ms (3.0 seconds) [AICMS-NF-001]")
        print(f"BENCHMARK STATUS:        {'PASS' if p90 <= 3000.0 else 'FAIL'}")
        print(f"{'='*70}\n")

        assert p90 <= 3000.0, f"p90 search latency {p90:.2f} ms exceeded 3000 ms SLA!"


def urllib_parse(s: str) -> str:
    import urllib.parse
    return urllib.parse.quote(s)
