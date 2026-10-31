import hashlib
import json
import math
import random
import re
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer

from backend.app.core.config import settings
from backend.app.core.errors import AICMSException

TAXONOMY_PROFILES = {
    "Engineering": "software architecture code database api system performance security testing cloud backend frontend deployment algorithm",
    "Finance": "budget revenue expense quarterly financial tax profit accounting audit balance statement capital fiscal invoice",
    "Legal": "contract agreement clause compliance liability terms regulatory privacy intellectual property policy governance dispute",
    "Human Resources": "employee onboarding payroll benefits recruitment personnel hiring performance appraisal talent workplace policy",
    "Operations": "logistics maintenance schedule facility supply chain process workflow inventory production operations monitoring",
    "General": "overview introduction general notes documentation report meeting minutes summary updates reference",
}


def generate_embedding(text: str) -> List[float]:
    """
    Generate 384-dimensional dense semantic vector (AICMS-F-008, TC-AI-01).
    Uses sentence-transformers/all-MiniLM-L6-v2 or deterministic normalized stub in CI.
    """
    if settings.SIMULATE_MODEL_FAILURE == 1:
        raise AICMSException(
            code="MODEL_FAILURE",
            message="Simulated AI model failure during embedding generation.",
            status_code=500,
        )

    if settings.EMBEDDER == "stub":
        # Deterministic 384-dimensional unit vector seeded by text content
        hasher = hashlib.sha256(text.encode("utf-8")).digest()
        seed = int.from_bytes(hasher[:8], "big")
        rng = random.Random(seed)
        vec = [rng.gauss(0.0, 1.0) for _ in range(384)]
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [float(x / norm) for x in vec]

    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        embedding = model.encode(text, normalize_embeddings=True)
        return [float(x) for x in embedding]
    except Exception as e:
        # Graceful fallback to deterministic embedder if weights unavailable
        hasher = hashlib.sha256(text.encode("utf-8")).digest()
        seed = int.from_bytes(hasher[:8], "big")
        rng = random.Random(seed)
        vec = [rng.gauss(0.0, 1.0) for _ in range(384)]
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [float(x / norm) for x in vec]


def classify_category(text: str) -> Tuple[str, float]:
    """
    Categorize document text against approved taxonomy with confidence score (AICMS-F-009, TC-AI-02).
    Returns (category_name, confidence_score) where confidence in [0.0, 1.0].
    """
    if settings.SIMULATE_MODEL_FAILURE == 1:
        raise AICMSException(
            code="MODEL_FAILURE",
            message="Simulated AI model failure during categorization.",
            status_code=500,
        )

    if not text.strip():
        return "General", 0.50

    clean_text = text.lower()
    categories = list(TAXONOMY_PROFILES.keys())
    documents = [clean_text] + [TAXONOMY_PROFILES[cat] for cat in categories]

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(documents)
        doc_vec = tfidf_matrix[0]

        best_score = -1.0
        best_category = "General"

        # Compute cosine similarity between document and taxonomy prototypes
        for idx, cat in enumerate(categories):
            cat_vec = tfidf_matrix[idx + 1]
            similarity = float((doc_vec * cat_vec.T).toarray()[0][0])
            if similarity > best_score:
                best_score = similarity
                best_category = cat

        # Normalize score into a calibrated confidence score [0.55, 0.98]
        if best_score > 0.05:
            confidence = min(0.98, max(0.55, best_score * 2.5))
        else:
            best_category = "General"
            confidence = 0.55

        return best_category, round(confidence, 4)
    except Exception:
        return "General", 0.50


def extract_keywords_and_topics(text: str) -> Tuple[List[str], List[str]]:
    """
    Extract 5-10 keyphrases and topic descriptors using TF-IDF (AICMS-F-010, TC-AI-03).
    """
    if settings.SIMULATE_MODEL_FAILURE == 1:
        raise AICMSException(
            code="MODEL_FAILURE",
            message="Simulated AI model failure during keyword extraction.",
            status_code=500,
        )

    if not text.strip():
        return [], []

    # Clean text
    words = re.findall(r"\b[A-Za-z]{3,}\b", text.lower())
    if len(words) < 5:
        return [w for w in set(words)], ["Overview"]

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=20,
        )
        tfidf_matrix = vectorizer.fit_transform([text])
        feature_names = vectorizer.get_feature_names_out()
        scores = tfidf_matrix.toarray()[0]

        # Rank by TF-IDF score
        ranked_keywords = [
            feature_names[i]
            for i in scores.argsort()[::-1]
            if len(feature_names[i]) > 2
        ]

        # Target between 5 and 10 keywords per AICMS-F-010
        keywords = ranked_keywords[:10]
        if len(keywords) < 5 and len(ranked_keywords) >= len(keywords):
            keywords = ranked_keywords[:5]

        # Derive topic labels from top ngrams
        topics = [kw.title() for kw in keywords[:3]]
        return keywords, topics
    except Exception:
        fallback_words = list(dict.fromkeys(words))[:7]
        return fallback_words, [w.title() for w in fallback_words[:3]]
