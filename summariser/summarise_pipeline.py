import sys

from data_loader import get_ayah_file_path
from llm_call import summarize_ayah


def summarize(surah, ayah):
    file_path = get_ayah_file_path(surah, ayah)
    summary = summarize_ayah(surah, ayah, file_path)

    print("\n=== SUMMARY ===\n")
    print(summary)

    return summary


def main():
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python summariser\\summarise_pipeline.py <surah> <ayah>")

    surah = int(sys.argv[1])
    ayah = int(sys.argv[2])
    summarize(surah, ayah)


if __name__ == "__main__":
    main()
