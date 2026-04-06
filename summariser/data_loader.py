import json
from pathlib import Path

BASE_FOLDER = Path("Ibn Kathir")


def load_ayah_data(surah, ayah):
    file_path = BASE_FOLDER / f"surah_{surah}" / f"ayah_{ayah}.json"

    if not file_path.exists():
        raise FileNotFoundError(f"Ayah file not found: {file_path}")

    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_ayah_text(surah, ayah):
    data = load_ayah_data(surah, ayah)
    return data["ayah"]


def load_ayah_tafsir(surah, ayah):
    data = load_ayah_data(surah, ayah)
    tafsir_texts = []

    for block in data.get("blocks", []):
        if block.get("type") == "tafsir":
            tafsir_texts.append(block["text"])

    return "\n".join(tafsir_texts)


def load_ayah_json_text(surah, ayah):
    data = load_ayah_data(surah, ayah)
    return json.dumps(data, ensure_ascii=False, indent=2)


def get_ayah_file_path(surah, ayah):
    file_path = BASE_FOLDER / f"surah_{surah}" / f"ayah_{ayah}.json"

    if not file_path.exists():
        raise FileNotFoundError(f"Ayah file not found: {file_path}")

    return file_path


def load_complete_ayah_text(surah, ayah):
    data = load_ayah_data(surah, ayah)
    parts = [
        f"Surah: {data['surah']}",
        f"Ayah: {data['ayah']}",
        f"Tafsir ID: {data.get('tafsir_id', '')}",
        "",
        "Blocks:",
    ]

    for block in data.get("blocks", []):
        block_type = block.get("type", "unknown")
        block_id = block.get("id", "")
        block_text = block.get("text", "")
        parts.append(f"[{block_type}] id={block_id}")
        parts.append(block_text)
        parts.append("")

    return "\n".join(parts).strip()
