import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path


CACHE_DIR = Path(__file__).resolve().parent / "cache"
SIMILARITY_THRESHOLD = float(os.getenv("RAG_CACHE_SIMILARITY_THRESHOLD", "0.92"))


def ensure_cache_dir():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def normalize_query(query):
    return " ".join(query.strip().lower().split())


def query_cache_key(query):
    normalized = normalize_query(query)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:24]


def get_cache_path(query):
    return CACHE_DIR / f"{query_cache_key(query)}.json"


def cosine_similarity(a, b):
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def serialize_results(results):
    serialized = []
    for score, item in results:
        serialized.append(
            {
                "score": score,
                "surah": item.get("surah"),
                "ayah": item.get("ayah"),
                "block_id": item.get("block_id"),
                "block_type": item.get("block_type"),
                "text": item.get("text"),
            }
        )
    return serialized


def deserialize_results(entry):
    results = []
    for item in entry.get("results", []):
        restored_item = {
            "surah": item.get("surah"),
            "ayah": item.get("ayah"),
            "block_id": item.get("block_id"),
            "block_type": item.get("block_type"),
            "text": item.get("text"),
        }
        results.append((item.get("score", 0.0), restored_item))
    return results


def load_cache_entry(query):
    cache_path = get_cache_path(query)
    if not cache_path.exists():
        return None

    with cache_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def iter_cache_entries():
    if not CACHE_DIR.exists():
        return

    for cache_file in sorted(CACHE_DIR.glob("*.json")):
        try:
            with cache_file.open("r", encoding="utf-8") as f:
                yield json.load(f)
        except (json.JSONDecodeError, OSError):
            continue


def find_similar_cache_entry(query_embedding, top_k=5, threshold=SIMILARITY_THRESHOLD):
    best_entry = None
    best_score = threshold

    for entry in iter_cache_entries() or []:
        cached_embedding = entry.get("query_embedding")
        cached_answer = entry.get("answer")
        cached_results = entry.get("results", [])

        if not cached_embedding or not cached_answer or len(cached_results) < top_k:
            continue

        score = cosine_similarity(query_embedding, cached_embedding)
        if score > best_score:
            best_score = score
            best_entry = entry

    return best_entry, best_score


def save_cache_entry(query, query_embedding, results, answer=None):
    ensure_cache_dir()
    cache_path = get_cache_path(query)
    now = datetime.now(timezone.utc).isoformat()
    existing_entry = load_cache_entry(query) or {}

    entry = {
        "query": query,
        "normalized_query": normalize_query(query),
        "query_embedding": query_embedding,
        "results": serialize_results(results),
        "result_count": len(results),
        "answer": answer if answer is not None else existing_entry.get("answer"),
        "created_at": existing_entry.get("created_at", now),
        "updated_at": now,
    }

    with cache_path.open("w", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False, indent=2)

    return entry
