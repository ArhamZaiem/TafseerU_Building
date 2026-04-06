import os
import json
import re
from pathlib import Path

from prompt_desing import build_prompt
from theme_connector.theme_index import build_theme_index

MODEL_NAME = os.getenv("OPENAI_CHAT_MODEL", "gpt-5.4")
CACHE_DIR = Path(__file__).resolve().parent / "cache"


def get_client():
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Install the 'openai' package before running this script: pip install openai") from exc

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set the OPENAI_API_KEY environment variable before running this script.")

    return OpenAI(api_key=api_key)


def get_cache_path(surah, ayah):
    return CACHE_DIR / f"surah_{surah}_ayah_{ayah}.json"


def parse_structured_output(output_text):
    themes = []
    summary = output_text.strip()

    match = re.search(
        r"Main Themes of the Ayah:\s*(.*?)\s*Summary:\s*(.*)",
        output_text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return {"main_themes": themes, "summary": summary, "output": output_text}

    themes_block = match.group(1).strip()
    summary = match.group(2).strip()

    for line in themes_block.splitlines():
        cleaned = re.sub(r"^\s*(?:[-*]|\d+[.)])\s*", "", line).strip()
        if cleaned:
            themes.append(cleaned)

    return {"main_themes": themes, "summary": summary, "output": output_text}


def load_cached_summary(surah, ayah):
    cache_path = get_cache_path(surah, ayah)
    if not cache_path.exists():
        return None

    with cache_path.open("r", encoding="utf-8") as f:
        cached = json.load(f)

    return cached.get("output") or cached.get("summary")


def save_cached_summary(surah, ayah, output_text):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = get_cache_path(surah, ayah)
    parsed = parse_structured_output(output_text)

    with cache_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "surah": surah,
                "ayah": ayah,
                "main_themes": parsed["main_themes"],
                "summary": parsed["summary"],
                "output": parsed["output"],
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    build_theme_index()


def summarize_ayah(surah, ayah, file_path):
    cached_summary = load_cached_summary(surah, ayah)
    if cached_summary:
        return cached_summary

    client = get_client()
    prompt = build_prompt(surah, ayah)

    with open(file_path, "rb") as f:
        uploaded_file = client.files.create(
            file=f,
            purpose="user_data",
        )

    response = client.responses.create(
        model=MODEL_NAME,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_file", "file_id": uploaded_file.id},
                ],
            }
        ],
    )

    try:
        client.files.delete(uploaded_file.id)
    except Exception:
        pass

    output_text = response.output_text
    save_cached_summary(surah, ayah, output_text)
    return output_text
