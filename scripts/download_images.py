"""
download_images.py
==================
Downloads royalty-free images from Wikimedia Commons for each round.
Run from the project root:

    python scripts/download_images.py

Images are saved to static/images/round_NN/image1.jpg and image2.jpg.
Existing files are skipped, so it is safe to re-run after manually
placing replacement images.

If a search returns no usable result, the script prints a warning and
continues. You can then manually download a replacement from:
  - https://pixabay.com (CC0, no attribution required)
  - https://unsplash.com (Unsplash License, free for most uses)
  - https://www.pexels.com (Pexels License, free for most uses)

Place the replacement file at the path shown in the warning message.
"""

import os
import sys
import time

import requests

# Fix Windows console Unicode issues
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WIKI_API = "https://commons.wikimedia.org/w/api.php"

# Wikimedia blocks requests without a descriptive User-Agent (returns 403).
HEADERS = {
    "User-Agent": (
        "WordGame/1.0 (https://github.com/jowakatima/Word_game; "
        "educational project) python-requests/2.32"
    )
}

# Project root is one level up from this script
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(ROOT_DIR, "static", "images")

# ---------------------------------------------------------------------------
# Map: (round_folder, image_filename_stem) -> Wikimedia Commons search query
# ---------------------------------------------------------------------------
IMAGE_MAP = [
    # Round 01 — sunflower (sun + flower)
    ("round_01", "image1", "sun sky blue clear day"),
    ("round_01", "image2", "sunflower single yellow bloom"),

    # Round 02 — starfish (star + fish)
    ("round_02", "image1", "five pointed star yellow shape"),
    ("round_02", "image2", "fish underwater ocean"),

    # Round 03 — eggplant (egg + plant)
    ("round_03", "image1", "chicken egg white single"),
    ("round_03", "image2", "green potted plant houseplant"),

    # Round 04 — football (foot + ball)
    ("round_04", "image1", "human bare foot"),
    ("round_04", "image2", "football soccer ball"),

    # Round 05 — raincoat (rain + coat)
    ("round_05", "image1", "rain drops falling puddle"),
    ("round_05", "image2", "coat jacket clothing wool"),

    # Round 06 — firefly (fire + fly)
    ("round_06", "image1", "candle flame fire close"),
    ("round_06", "image2", "Musca domestica housefly"),

    # Round 07 — teapot (tea + pot)
    ("round_07", "image1", "teacup"),
    ("round_07", "image2", "clay pot terracotta cooking"),

    # Round 08 — snowball (snow + ball)
    ("round_08", "image1", "snow white winter ground"),
    ("round_08", "image2", "ball toy round"),

    # Round 09 — butterfly (butter + fly)
    ("round_09", "image1", "butter dairy"),
    ("round_09", "image2", "fly insect wings macro"),

    # Round 10 — doorbell (door + bell)
    ("round_10", "image1", "wooden door entrance front"),
    ("round_10", "image2", "cowbell"),
]


# ---------------------------------------------------------------------------
# Wikimedia Commons helpers
# ---------------------------------------------------------------------------

def search_wikimedia(query, limit=5):
    """Return a list of File: titles matching the query."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srnamespace": "6",   # File namespace (images only)
        "srlimit": limit,
        "format": "json",
    }
    try:
        resp = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        results = resp.json().get("query", {}).get("search", [])
        return [r["title"] for r in results]
    except Exception as exc:
        print(f"    Search error: {exc}")
        return []


def get_image_info(file_title):
    """Return (url, extension) for a File: title, or (None, None)."""
    params = {
        "action": "query",
        "titles": file_title,
        "prop": "imageinfo",
        "iiprop": "url|mime",
        "format": "json",
    }
    try:
        resp = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        pages = resp.json().get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [{}])
            if info:
                entry = info[0]
                mime = entry.get("mime", "")
                url = entry.get("url")
                if "jpeg" in mime:
                    return url, "jpg"
                if "png" in mime:
                    return url, "png"
    except Exception as exc:
        print(f"    URL fetch error: {exc}")
    return None, None


def download_file(url, dest_path):
    """Stream-download a URL to dest_path."""
    resp = requests.get(url, headers=HEADERS, timeout=30, stream=True)
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Word Game — Image Downloader")
    print("=" * 50)

    success = 0
    skipped = 0
    failed = []

    for folder, name, query in IMAGE_MAP:
        dest_dir = os.path.join(IMAGES_DIR, folder)
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, f"{name}.jpg")

        if os.path.exists(dest_path):
            print(f"  [SKIP] {folder}/{name}.jpg  (already exists)")
            skipped += 1
            continue

        print(f"  [SEARCH] {folder}/{name}  query='{query}'")
        titles = search_wikimedia(query, limit=5)

        downloaded = False
        for title in titles:
            url, ext = get_image_info(title)
            if not url:
                continue
            # Always save as .jpg (rounds.json paths all use .jpg)
            try:
                download_file(url, dest_path)
                size_kb = os.path.getsize(dest_path) // 1024
                print(f"    [OK] {title}  ({size_kb} KB, {ext})")
                downloaded = True
                success += 1
                break
            except Exception as exc:
                print(f"    [FAIL] {title}: {exc}")

        if not downloaded:
            print(f"    [WARN] No image found for {folder}/{name}.jpg")
            print(f"           Place a JPEG manually at: {dest_path}")
            failed.append(f"{folder}/{name}.jpg")

        time.sleep(0.6)  # be polite to the API

    print()
    print("=" * 50)
    print(f"Done: {success} downloaded, {skipped} skipped, {len(failed)} failed")
    if failed:
        print("\nManually provide images for:")
        for path in failed:
            print(f"  static/images/{path}")


if __name__ == "__main__":
    main()
