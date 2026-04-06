import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time

# 📊 SURAH → AYAH COUNT
SURAH_AYAH_COUNT = {
    1: 7,
    2: 286,
    3: 200,
    4: 176,
    5: 120,
    6: 165,
    7: 206,
    8: 75,
    9: 129,
    10: 109,
    11: 123,
    12: 111,
    13: 43,
    14: 52,
    15: 99,
    16: 128,
    17: 111,
    18: 110,
    19: 98,
    20: 135,
    21: 112,
    22: 78,
    23: 118,
    24: 64,
    25: 77,
    26: 227,
    27: 93,
    28: 88,
    29: 69,
    30: 60,
    31: 34,
    32: 30,
    33: 73,
    34: 54,
    35: 45,
    36: 83,
    37: 182,
    38: 88,
    39: 75,
    40: 85,
    41: 54,
    42: 53,
    43: 89,
    44: 59,
    45: 37,
    46: 35,
    47: 38,
    48: 29,
    49: 18,
    50: 45,
    51: 60,
    52: 49,
    53: 62,
    54: 55,
    55: 78,
    56: 96,
    57: 29,
    58: 22,
    59: 24,
    60: 13,
    61: 14,
    62: 11,
    63: 11,
    64: 18,
    65: 12,
    66: 12,
    67: 30,
    68: 52,
    69: 52,
    70: 44,
    71: 28,
    72: 28,
    73: 20,
    74: 56,
    75: 40,
    76: 31,
    77: 50,
    78: 40,
    79: 46,
    80: 42,
    81: 29,
    82: 19,
    83: 36,
    84: 25,
    85: 22,
    86: 17,
    87: 19,
    88: 26,
    89: 30,
    90: 20,
    91: 15,
    92: 21,
    93: 11,
    94: 8,
    95: 8,
    96: 19,
    97: 5,
    98: 8,
    99: 8,
    100: 11,
    101: 11,
    102: 8,
    103: 3,
    104: 9,
    105: 5,
    106: 4,
    107: 7,
    108: 3,
    109: 6,
    110: 3,
    111: 5,
    112: 4,
    113: 5,
    114: 6,
}


# 🔧 TEXT CLEANING
def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([،.؟:])", r"\1", text)
    return text.strip()


# 🧠 EXTRACT ELEMENTS
def extract_elements(html):
    soup = BeautifulSoup(html, "html.parser")
    elements = []

    for el in soup.find_all(["tafsir", "hadeeth", "ayah"]):
        text = el.get_text(separator=" ", strip=True)
        text = clean_text(text)

        if not text:
            continue

        elements.append({"type": el.name, "text": text})

    return elements


# 🔥 MERGE TAFSIR BLOCKS
def merge_tafsir_blocks(elements):
    merged = []
    buffer = ""

    for el in elements:
        if el["type"] == "tafsir":
            buffer += " " + el["text"]
        else:
            if buffer:
                merged.append({"type": "tafsir", "text": buffer.strip()})
                buffer = ""

            merged.append(el)

    if buffer:
        merged.append({"type": "tafsir", "text": buffer.strip()})

    return merged


# 🌐 FETCH WITH RETRY
def fetch_tafsir(surah, ayah, tafsir_id=7, retries=3):
    url = "https://greattafsirs.com/Tafsir_Library.aspx"

    params = {
        "LanguageID": 1,
        "SoraNo": surah,
        "AyahNo": ayah,
        "MadhabNo": -1,
        "TafsirNo": tafsir_id,
    }

    headers = {"User-Agent": "Mozilla/5.0"}

    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.text

        except Exception as e:
            print(f"⚠️ Retry {attempt + 1} failed: {e}")
            time.sleep(2)

    return None


# 💾 SAVE DATA
def save_data(data, surah, ayah):
    folder = f"Ibn Kathir/surah_{surah}"
    os.makedirs(folder, exist_ok=True)

    file_path = f"{folder}/ayah_{ayah}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ⏭ CHECK IF EXISTS
def already_exists(surah, ayah):
    path = f"Ibn Kathir/surah_{surah}/ayah_{ayah}.json"
    return os.path.exists(path)


# 🚀 PROCESS ONE AYAH
def process_ayah(surah, ayah):
    html = fetch_tafsir(surah, ayah)

    if not html:
        print(f"❌ Failed: {surah}:{ayah}")
        return

    elements = extract_elements(html)

    if not elements:
        print(f"⛔ No data: {surah}:{ayah}")
        return

    merged = merge_tafsir_blocks(elements)

    final_data = {"surah": surah, "ayah": ayah, "tafsir_id": 7, "blocks": merged}

    save_data(final_data, surah, ayah)

    print(f"✅ Saved: Surah {surah}, Ayah {ayah}")


# 🔁 MAIN LOOP (RUN IN BATCHES FIRST)
def run_scraper(start_surah=1, end_surah=114):
    for surah in range(start_surah, end_surah + 1):
        max_ayah = SURAH_AYAH_COUNT[surah]

        print(f"\n📖 Starting Surah {surah}...\n")

        for ayah in range(1, max_ayah + 1):
            if already_exists(surah, ayah):
                print(f"⏭ Skipped {surah}:{ayah}")
                continue

            process_ayah(surah, ayah)
            time.sleep(1.5)


# ▶️ START HERE
run_scraper(25, 25)  # change range gradually
