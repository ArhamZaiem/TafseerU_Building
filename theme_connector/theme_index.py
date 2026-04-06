import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_DIR = PROJECT_ROOT / "summariser" / "cache"
INDEX_FILE = Path(__file__).resolve().parent / "theme_index.json"


def normalize_theme(theme):
    cleaned = theme.strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"[^\w\s-]", "", cleaned)
    return cleaned.strip()


def build_theme_index():
    ayahs = []
    themes = {}

    if not CACHE_DIR.exists():
        index = {"ayahs": [], "themes": {}}
        with INDEX_FILE.open("w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        return index

    for cache_file in sorted(CACHE_DIR.glob("*.json")):
        with cache_file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        surah = data.get("surah")
        ayah = data.get("ayah")
        main_themes = data.get("main_themes", [])

        if surah is None or ayah is None:
            continue

        ayah_entry = {
            "surah": surah,
            "ayah": ayah,
            "main_themes": main_themes,
        }
        ayahs.append(ayah_entry)

        for theme in main_themes:
            normalized = normalize_theme(theme)
            if not normalized:
                continue

            themes.setdefault(normalized, []).append({"surah": surah, "ayah": ayah})

    for theme_name, references in themes.items():
        unique_refs = []
        seen = set()
        for ref in references:
            key = (ref["surah"], ref["ayah"])
            if key in seen:
                continue
            seen.add(key)
            unique_refs.append(ref)
        themes[theme_name] = unique_refs

    index = {"ayahs": ayahs, "themes": themes}
    with INDEX_FILE.open("w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    return index


if __name__ == "__main__":
    build_theme_index()
