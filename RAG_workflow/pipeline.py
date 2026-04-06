import sys

try:
    from RAG_workflow.llm_generation import get_cached_or_generate_answer
    from RAG_workflow.test_embedding import load_embeddings
except ModuleNotFoundError:
    from llm_generation import get_cached_or_generate_answer
    from test_embedding import load_embeddings


def ask(query, top_k=5):
    embeddings = load_embeddings()
    answer = get_cached_or_generate_answer(query, embeddings, top_k=top_k)

    print("\n=== ANSWER ===\n")
    print(answer)

    return answer


def main():
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python RAG_workflow\\pipeline.py "your question here"')

    query = " ".join(sys.argv[1:])
    ask(query)


if __name__ == "__main__":
    main()
