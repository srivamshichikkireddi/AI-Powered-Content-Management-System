import urllib.parse
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app
from backend.app.scripts.seed_demo import seed_demo
from backend.tests.benchmarks.benchmark_corpus import SEARCH_BENCHMARK_QUERIES


@pytest.mark.asyncio
async def test_search_relevance_precision_at_5_benchmark():
    """
    Information Retrieval Quality Benchmark: Evaluate Precision@5 and Mean Reciprocal Rank (MRR)
    across reviewed query-document relevance benchmarks (SRS §5.2).
    Target: A relevant document in top 5 results for at least 80% of queries (Precision@5 >= 80%).
    """
    await seed_demo()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Authenticate
        auth_resp = await client.post("/api/v1/auth/login", json={"username": "regular_user", "password": "UserPass123!"})
        assert auth_resp.status_code == 200
        token = auth_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        print(f"\n{'='*70}\n[IR BENCHMARK] Search Relevance & Precision@5 Evaluation\nEvaluating {len(SEARCH_BENCHMARK_QUERIES)} reviewed natural language queries\n{'='*70}")

        relevant_in_top_5 = 0
        reciprocal_ranks = []

        for q_item in SEARCH_BENCHMARK_QUERIES:
            q_text = q_item["query"]
            target_cat = q_item["target_category"]
            exp_match = q_item["expected_match"].lower()

            encoded_q = urllib.parse.quote(q_text)
            resp = await client.get(f"/api/v1/search?q={encoded_q}&limit=5", headers=headers)
            assert resp.status_code == 200
            data = resp.json()
            results = data["results"]

            # Check if top results contain relevant document
            hit_rank = 0
            for rank, r in enumerate(results, 1):
                if target_cat.lower() in (r["category_name"] or "").lower() or exp_match in r["title"].lower():
                    hit_rank = rank
                    break

            if hit_rank > 0 and hit_rank <= 5:
                relevant_in_top_5 += 1
                reciprocal_ranks.append(1.0 / hit_rank)
            else:
                reciprocal_ranks.append(0.0)

            status_mark = f"Rank #{hit_rank}" if hit_rank > 0 else "Miss"
            print(f"[{status_mark:<7}] Query: \"{q_text:<45}\" -> Target: {target_cat}")

        precision_at_5 = (relevant_in_top_5 / len(SEARCH_BENCHMARK_QUERIES)) * 100.0
        mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)

        print(f"\n{'-'*70}")
        print(f"Total Reviewed Queries:  {len(SEARCH_BENCHMARK_QUERIES)}")
        print(f"Relevant Hit in Top 5:   {relevant_in_top_5}/{len(SEARCH_BENCHMARK_QUERIES)}")
        print(f"Precision@5 Coverage:    {precision_at_5:.2f}%")
        print(f"Mean Reciprocal Rank:    {mrr:.4f}")
        print(f"{'-'*70}")
        print(f"TARGET REQUIREMENT:      Precision@5 >= 80.00% (SRS §5.2 Quality Benchmark)")
        print(f"BENCHMARK STATUS:        {'PASS' if precision_at_5 >= 80.0 else 'FAIL'}")
        print(f"{'='*70}\n")

        assert precision_at_5 >= 80.0, f"Precision@5 {precision_at_5:.2f}% below 80% target!"
