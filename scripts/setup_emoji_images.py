"""
setup_emoji_images.py
=====================
Downloads emoji images from OpenMoji (https://openmoji.org, CC BY-SA 4.0)
for each round component. Images are 618x618 PNG files.

Run from the project root:
    python scripts/setup_emoji_images.py

Existing files are skipped. To force a re-download, delete the target file first.
"""

import os
import sys
import time

import requests

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(ROOT_DIR, "static", "images")

BASE_URL = "https://raw.githubusercontent.com/hfg-gmuend/openmoji/master/color/618x618/{}.png"
HEADERS = {"User-Agent": "WordGame/1.0 (https://github.com/jowakatima/Word_game)"}

# ---------------------------------------------------------------------------
# (round_folder, image1_codepoint, image2_codepoint)
# Codepoints are uppercase hex, multi-codepoint joined with "-"
# ---------------------------------------------------------------------------
EMOJI_MAP = [
    # Rounds 01-10 (original rounds, new emoji images)
    ("round_01", "2600",      "1F338"),       # sun + flower         = sunflower
    ("round_02", "2B50",      "1F41F"),       # star + fish          = starfish
    ("round_03", "1F95A",     "1FAB4"),       # egg + potted plant   = eggplant
    ("round_04", "1F9B6",     "26BD"),        # foot + soccer ball   = football
    ("round_05", "1F327",     "1F9E5"),       # rain cloud + coat    = raincoat
    ("round_06", "1F525",     "1FAB0"),       # fire + fly           = firefly
    ("round_07", "1F375",     "1F372"),       # teacup + pot         = teapot
    ("round_08", "2744", "1F3BE"),       # snowflake + tennis ball = snowball
    ("round_09", "1F9C8",     "1FAB0"),       # butter + fly         = butterfly
    ("round_10", "1F6AA",     "1F514"),       # door + bell          = doorbell
    # Rounds 11-30 (new rounds)
    ("round_11", "1F36F",     "1F41D"),       # honey + bee          = honeybee
    ("round_12", "1F332",     "1F34E"),       # pine tree + apple    = pineapple
    ("round_13", "1F4A7",     "1F348"),       # water drop + melon   = watermelon
    ("round_14", "1F415",     "1F3E0"),       # dog + house          = doghouse
    ("round_15", "2615",      "1F382"),       # cup + cake           = cupcake
    ("round_16", "1F431",     "1F41F"),       # cat + fish           = catfish
    ("round_17", "1F409",     "1FAB0"),       # dragon + fly         = dragonfly
    ("round_18", "1F4DA",     "1F41B"),       # books + worm/bug     = bookworm
    ("round_19", "2744", "1F468"),       # snowflake + man      = snowman
    ("round_20", "1F30A",     "1F41A"),       # wave/sea + shell     = seashell
    ("round_21", "1F319",     "1F4A1"),       # moon + light bulb    = moonlight
    ("round_22", "26FA",      "1F525"),       # tent/camp + fire     = campfire
    ("round_23", "1F947",     "1F41F"),       # gold medal + fish    = goldfish
    ("round_24", "1F441",     "1F3C0"),       # eye + basketball     = eyeball
    ("round_25", "1F5A4",     "1F426"),       # black heart + bird   = blackbird
    ("round_26", "1F404",     "1F466"),       # cow + boy            = cowboy
    ("round_27", "1F525",     "1F468"),       # fire + man           = fireman
    ("round_28", "1F3D6",     "1F3F0"),       # beach + castle       = sandcastle
    ("round_29", "2600",      "1F453"),       # sun + glasses        = sunglasses
    ("round_30", "2B50",      "1F4A1"),       # star + light bulb    = starlight
    # Rounds 31-50
    ("round_31", "1F499",     "1F353"),       # blue heart + strawberry = blueberry
    ("round_32", "1F33D",     "1F33E"),       # corn + wheat/sheaf   = cornfield
    ("round_33", "1F373",     "1F4DA"),       # frying pan + books   = cookbook
    ("round_34", "1F33F",     "1F997"),       # herb + cricket       = grasshopper
    ("round_35", "1F347",     "1F34A"),       # grapes + orange      = grapefruit
    ("round_36", "1F91A",     "1F45C"),       # raised hand + handbag = handbag
    ("round_37", "1F321",     "1F415"),       # thermometer + dog    = hotdog
    ("round_38", "1F9CA",     "26F0"),        # ice cube + mountain  = iceberg
    ("round_39", "1F5DD",     "1F573"),       # key + hole           = keyhole
    ("round_40", "1F371",     "1F4E6"),       # bento box + package  = lunchbox
    ("round_41", "1F327",     "1F380"),       # rain cloud + ribbon bow = rainbow
    ("round_42", "26F8",      "1FAB5"),       # ice skate + wood log = skateboard
    ("round_43", "1F9B7",     "1F58C"),       # tooth + paintbrush   = toothbrush
    ("round_44", "1F4A7",     "1F342"),       # water drop + fallen leaf = waterfall
    ("round_45", "1F64F",     "1F9B4"),       # praying hands + bone = wishbone
    ("round_46", "1F4A5",     "1F33D"),       # explosion + corn     = popcorn
    ("round_47", "1F41C",     "26F0"),        # ant + mountain       = anthill
    ("round_48", "1F33F",     "1F437"),       # herb/hedge + pig     = hedgehog
    ("round_49", "1F499",     "1F514"),       # blue heart + bell    = bluebell
    ("round_50", "1F375",     "1F944"),       # teacup + spoon       = teaspoon
]


def download(url, dest_path):
    r = requests.get(url, headers=HEADERS, timeout=30, stream=True)
    r.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)


def main():
    print("Word Game — Emoji Image Setup (OpenMoji)")
    print("=" * 50)
    ok = skip = fail = 0
    failed = []

    for folder, cp1, cp2 in EMOJI_MAP:
        dest_dir = os.path.join(IMAGES_DIR, folder)
        os.makedirs(dest_dir, exist_ok=True)

        for num, cp in (("image1", cp1), ("image2", cp2)):
            dest = os.path.join(dest_dir, f"{num}.png")
            if os.path.exists(dest):
                print(f"  [SKIP] {folder}/{num}.png")
                skip += 1
                continue

            url = BASE_URL.format(cp)
            print(f"  [GET]  {folder}/{num}.png  ({cp})")
            try:
                download(url, dest)
                kb = os.path.getsize(dest) // 1024
                print(f"         OK  {kb} KB")
                ok += 1
            except Exception as e:
                print(f"         FAIL: {e}")
                failed.append(f"{folder}/{num}.png  [{cp}]")
                fail += 1
            time.sleep(0.3)

    print()
    print("=" * 50)
    print(f"Done: {ok} downloaded, {skip} skipped, {fail} failed")
    if failed:
        print("\nFailed images:")
        for p in failed:
            print(f"  {p}")


if __name__ == "__main__":
    main()
