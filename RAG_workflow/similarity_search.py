import math
import sys

try:
    from RAG_workflow.cache import deserialize_results, load_cache_entry
    from RAG_workflow.test_embedding import get_client, get_embedding, load_embeddings
except ModuleNotFoundError:
    from cache import deserialize_results, load_cache_entry
    from test_embedding import get_client, get_embedding, load_embeddings


def cosine_similarity(a, b):
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def search(query, embeddings, top_k=5, query_embedding=None, use_cache=True):
    if use_cache:
        cached_entry = load_cache_entry(query)
        if cached_entry and len(cached_entry.get("results", [])) >= top_k:
            return deserialize_results(cached_entry)[:top_k]

    query_emb = query_embedding
    if query_emb is None:
        client = get_client()
        query_emb = get_embedding(client, query)

    results = []

    for item in embeddings:
        score = cosine_similarity(query_emb, item["embedding"])
        results.append((score, item))

    results.sort(key=lambda x: x[0], reverse=True)
    return results[:top_k]


def main():
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python similarity_search.py "your query here"')

    query = " ".join(sys.argv[1:])
    embeddings = load_embeddings()
    results = search(query, embeddings)

    for rank, (score, item) in enumerate(results, start=1):
        print(
            f"{rank}. score={score:.4f} surah={item['surah']} ayah={item['ayah']} "
            f"block_type={item.get('block_type', 'unknown')} block_id={item['block_id']}"
        )
        print(item["text"])
        print()


if __name__ == "__main__":
    main()
