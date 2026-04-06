import json
import os
from pathlib import Path

WORKFLOW_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = WORKFLOW_DIR.parent
BASE_FOLDER = PROJECT_ROOT / "Ibn Kathir" / "surah_1"
OUTPUT_FILE = WORKFLOW_DIR / "embeddings1.json"
LEGACY_OUTPUT_FILE = WORKFLOW_DIR / "embeddings.json"


def get_client():
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Install the 'openai' package before running this script: pip install openai") from exc

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set the OPENAI_API_KEY environment variable before running this script.")
    return OpenAI(api_key=api_key)


def get_embedding(client, text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def build_embeddings():
    if not BASE_FOLDER.exists():
        raise FileNotFoundError(f"Base folder not found: {BASE_FOLDER}")

    client = get_client()
    embedding_store = []
    block_counts = {}

    for path in sorted(BASE_FOLDER.glob("*.json")):
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        for block in data.get("blocks", []):
            block_type = block.get("type")
            block_text = block.get("text")

            if not block_type or not block_text:
                continue

            block_counts[block_type] = block_counts.get(block_type, 0) + 1
            embedding_store.append(
                {
                    "embedding": get_embedding(client, block_text),
                    "text": block_text,
                    "surah": data["surah"],
                    "ayah": data["ayah"],
                    "block_id": block["id"],
                    "block_type": block_type,
                }
            )

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(embedding_store, f, ensure_ascii=False, indent=2)

    print(f"Embeddings built: {len(embedding_store)} blocks saved to {OUTPUT_FILE}")
    if block_counts:
        print("Embedded block types:")
        for block_type, count in sorted(block_counts.items()):
            print(f"- {block_type}: {count}")


if __name__ == "__main__":
    build_embeddings()


def load_embeddings():
    embeddings_file = OUTPUT_FILE if OUTPUT_FILE.exists() else LEGACY_OUTPUT_FILE
    with embeddings_file.open("r", encoding="utf-8") as f:
        return json.load(f)
