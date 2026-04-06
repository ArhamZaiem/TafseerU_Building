import os
import json

BASE_FOLDER = "Ibn Kathir"
INDEX_FILE = "index.json"


def build_index():
    index = {}

    for root, dirs, files in os.walk(BASE_FOLDER):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)

                    surah = data.get("surah")
                    ayah = data.get("ayah")

                    if surah and ayah:
                        key = f"{surah}_{ayah}"
                        index[key] = file_path

                except Exception as e:
                    print(f"❌ Skipping: {file_path} ({e})")

    # save index
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

    print("✅ Index created successfully")


if __name__ == "__main__":
    build_index()



with open("index.json", "r") as f:
    index = json.load(f)

def get_ayah(surah, ayah):
    key = f"{surah}_{ayah}"
    path = index.get(key)

    if not path:
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
    


data = get_ayah(2, 2)
print(data["blocks"])