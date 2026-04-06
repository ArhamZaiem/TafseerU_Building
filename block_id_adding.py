import os
import json

BASE_FOLDER = "Ibn Kathir"  # your root folder


def add_block_ids(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    surah = data.get("surah")
    ayah = data.get("ayah")

    if "blocks" not in data:
        return

    updated = False

    for i, block in enumerate(data["blocks"], start=1):
        if "id" not in block:
            block["id"] = f"{surah}_{ayah}_{block['type']}_b{i}"
            updated = True

    if updated:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ Updated: {file_path}")
    else:
        print(f"⏭ Already done: {file_path}")


def process_all_files():
    for root, dirs, files in os.walk(BASE_FOLDER):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                add_block_ids(file_path)


if __name__ == "__main__":
    process_all_files()