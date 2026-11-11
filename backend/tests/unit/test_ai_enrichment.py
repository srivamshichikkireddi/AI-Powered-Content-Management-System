import math
import pytest

from backend.app.core.config import settings
from backend.app.core.errors import AICMSException
from backend.app.services.ai_service import (
    classify_category,
    extract_keywords_and_topics,
    generate_embedding,
)


def test_embedding_dimensions_and_norm_tc_ai_01():
    """
    TC-AI-01: Verify semantic embedding vector generation.
    - Dimensions must be 384 (all-MiniLM-L6-v2 specification).
    - Vector must be L2-normalized (magnitude == 1.0).
    - Deterministic across identical input text.
    """
    sample_text = "FastAPI backend services integrated with PostgreSQL and pgvector for semantic retrieval."
    vec1 = generate_embedding(sample_text)
    vec2 = generate_embedding(sample_text)

    assert len(vec1) == 384
    assert len(vec2) == 384
    assert vec1 == vec2  # Deterministic representation

    # Check L2 unit norm
    norm = math.sqrt(sum(x * x for x in vec1))
    assert abs(norm - 1.0) < 1e-4


def test_category_classification_confidence_tc_ai_02():
    """
    TC-AI-02: Auto-categorization against approved taxonomy with confidence score.
    """
    # 1. Engineering sample
    eng_text = "Software engineering architecture, microservices API implementation, unit testing and continuous integration pipeline."
    cat_eng, conf_eng = classify_category(eng_text)
    assert cat_eng == "Engineering"
    assert 0.0 <= conf_eng <= 1.0

    # 2. Finance sample
    fin_text = "Fiscal year budget allocation, quarterly financial revenue, accounting balance statement, audit expense reports."
    cat_fin, conf_fin = classify_category(fin_text)
    assert cat_fin == "Finance"
    assert 0.0 <= conf_fin <= 1.0

    # 3. Legal sample
    legal_text = "Master services agreement terms and conditions, contractual liability clause, intellectual property governance and dispute settlement."
    cat_legal, conf_legal = classify_category(legal_text)
    assert cat_legal == "Legal"
    assert 0.0 <= conf_legal <= 1.0


def test_keyword_and_topic_extraction_tc_ai_03():
    """
    TC-AI-03: Keyword and topic extraction returns between 5 and 10 keywords and topic descriptor.
    """
    article = (
        "PostgreSQL with pgvector provides efficient vector similarity search using cosine distance. "
        "The AI-Powered Content Management System indexes document embeddings and enables natural language query matching. "
        "Full text search and semantic vector indexing combine to deliver high precision and recall for document discovery."
    )
    keywords, topics = extract_keywords_and_topics(article)

    assert 5 <= len(keywords) <= 10
    assert len(topics) >= 1
    assert any("search" in kw or "vector" in kw or "indexing" in kw or "embeddings" in kw for kw in keywords)


def test_simulate_model_failure_flag():
    """Verify SIMULATE_MODEL_FAILURE=1 flag raises structured error."""
    settings.SIMULATE_MODEL_FAILURE = 1
    try:
        with pytest.raises(AICMSException) as exc_info:
            generate_embedding("Test text")
        assert exc_info.value.code == "MODEL_FAILURE"
    finally:
        settings.SIMULATE_MODEL_FAILURE = 0
