import os
import re
import sys
from collections import defaultdict

try:
    from RAG_workflow.cache import (
        deserialize_results,
        find_similar_cache_entry,
        load_cache_entry,
        save_cache_entry,
    )
    from RAG_workflow.similarity_search import search
    from RAG_workflow.test_embedding import get_client, get_embedding, load_embeddings
except ModuleNotFoundError:
    from cache import deserialize_results, find_similar_cache_entry, load_cache_entry, save_cache_entry
    from similarity_search import search
    from test_embedding import get_client, get_embedding, load_embeddings

MODEL_NAME = "gpt-5.4"
DEBUG_PROMPT = os.getenv("DEBUG_PROMPT", "").lower() in {"1", "true", "yes", "on"}


def block_sort_key(item):
    block_id = item.get("block_id", "")
    match = re.search(r"_b(\d+)$", block_id)
    if match:
        return (0, int(match.group(1)), block_id)
    return (1, 0, block_id)


def expand_results_with_ayah_context(results, embeddings):
    ayah_keys = {(item["surah"], item["ayah"]) for _, item in results}
    retrieved_scores = {
        item["block_id"]: score for score, item in results
    }
    expanded = []

    for item in embeddings:
        key = (item["surah"], item["ayah"])
        if key not in ayah_keys:
            continue

        expanded.append((retrieved_scores.get(item["block_id"]), item))

    return expanded


def build_context(results, embeddings=None):
    grouped = defaultdict(list)
    context_results = expand_results_with_ayah_context(results, embeddings) if embeddings else results

    for score, item in context_results:
        key = (item["surah"], item["ayah"])
        grouped[key].append((score, item))

    ayah_sections = []
    for surah, ayah in sorted(grouped):
        blocks = sorted(grouped[(surah, ayah)], key=lambda pair: block_sort_key(pair[1]))
        lines = [f"Surah {surah}, Ayah {ayah}"]

        for score, item in blocks:
            block_type = item.get("block_type", "unknown")
            if score is None:
                lines.append(f"{block_type}: {item['text']}")
            else:
                lines.append(f"{block_type} (retrieved, score: {score:.4f}): {item['text']}")

        ayah_sections.append("\n".join(lines))

    return "\n\n".join(ayah_sections)


def generate_answer(query, results, embeddings=None):
    client = get_client()
    context = build_context(results, embeddings=embeddings)

    prompt = f"""
Task: Summarize this into English 



Rules:
- Analyze the file attached completely 
- Summarize in complete
- if there is a spritual element in it or anything related to practical affairs or action related affairs do not forget to include it, if there is only then.
- do not leave out anything importing which should be covered it in, with regards to the sprituality, diferrence of opinions, the action related part, present them in a summarised form though, following the command given just above this 
- do not divert from the original meaning
- do not miss out on the important points given the context of the readers
- be faithful in the translation and do not hallucinate
- do not break sentences or use incomplete sentences
- statements should be easily understandable as given the context of the audience
- this will be read by locals and laymen so do not use complex language
- also maintain the scholarly tone but as i said make it more reader's focused language 
- if there's a need for bullet points for making the understanding easy use that, *do not go overboard with bullet points*
- i want the usage of pragraph style too, but I want bullet points too for better readability and understanding, so I am leaving it onto you, but do not go overboard with either of the too
- give the output directly, without stating anything else

Context:
{context}

Question:
{query}

Answer in English with references.
"""

    if DEBUG_PROMPT:
        print("\n=== RETRIEVED RESULTS ===\n")
        for score, item in results:
            print(
                f"score={score:.4f} surah={item['surah']} "
                f"ayah={item['ayah']} block_type={item.get('block_type', 'unknown')} "
                f"block_id={item['block_id']}"
            )
            print(item["text"])
            print()

        print("\n=== RETRIEVED CONTEXT ===\n")
        print(context)

        print("\n=== FULL PROMPT SENT TO API ===\n")
        print(prompt)
        print()

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
        temperature=0.2,
    )

    return response.output_text


def get_cached_or_generate_answer(query, embeddings, top_k=5):
    client = get_client()
    query_embedding = get_embedding(client, query)

    exact_entry = load_cache_entry(query)
    if exact_entry and exact_entry.get("answer") and len(exact_entry.get("results", [])) >= top_k:
        if DEBUG_PROMPT:
            print("\n=== RAG CACHE HIT ===\n")
            print("Using exact cached answer.")
        return exact_entry["answer"]

    similar_entry, similarity = find_similar_cache_entry(query_embedding, top_k=top_k)
    if similar_entry:
        if DEBUG_PROMPT:
            matched_query = similar_entry.get("query", "")
            print("\n=== RAG CACHE HIT ===\n")
            print(
                f"Using similar cached answer "
                f"(similarity={similarity:.4f}, cached_query={matched_query!r})"
            )
        return similar_entry["answer"]

    if exact_entry and len(exact_entry.get("results", [])) >= top_k:
        results = deserialize_results(exact_entry)[:top_k]
    else:
        results = search(query, embeddings, top_k=top_k, query_embedding=query_embedding, use_cache=False)
        save_cache_entry(query, query_embedding, results)

    answer = generate_answer(query, results, embeddings=embeddings)
    save_cache_entry(query, query_embedding, results, answer=answer)
    return answer


def main():
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python RAG_workflow\\llm_generation.py "your question here"')

    query = " ".join(sys.argv[1:])
    embeddings = load_embeddings()
    answer = get_cached_or_generate_answer(query, embeddings, top_k=5)
    print(answer)


if __name__ == "__main__":
    main()
