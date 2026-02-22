# Word Game

A local web-based image compound-word guessing game built with Python + Flask.

Two images are shown per round. Type the compound word they represent together
(for example: egg + plant = **eggplant**). Wrong guesses are tracked, a hint
appears after 2 incorrect attempts, and the round ends in a loss after 4.

---

## Quick Start

### 1. Install dependencies

```bash
python -m venv .venv
# Windows (Git Bash / PowerShell)
source .venv/Scripts/activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Download round images (one-time setup)

```bash
python scripts/download_images.py
```

This fetches 20 royalty-free JPEG images from Wikimedia Commons and saves them
to `static/images/round_NN/`. Already-downloaded files are skipped on
subsequent runs, so you can safely re-run if something fails.

If any image download fails, the script will tell you the exact path to place
a manual replacement (JPEG, any resolution — it will be cropped to fit).
Good free sources: [Pixabay](https://pixabay.com), [Unsplash](https://unsplash.com),
[Pexels](https://www.pexels.com).

### 3. Start the server

```bash
flask --app app.py run --debug
```

### 4. Open the game

Open your browser and go to: **http://127.0.0.1:5000**

Or double-click **OPEN_GAME.url** in the project folder to open it directly.

> The server must be running for the link to work. Stop it any time with Ctrl+C.

---

## Game Rules

| Situation | Outcome |
|-----------|---------|
| Correct answer | Round won — score saved |
| 2 wrong guesses | Text hint revealed |
| 4 wrong guesses | Round lost — score saved |

- Results from your last 5 rounds are shown on the main menu.
- Rounds are picked randomly within a session; all 10 play before any repeats.

---

## Project Structure

```
Word_game/
├── app.py                  Flask application (all routes and game logic)
├── requirements.txt        Python dependencies
├── OPEN_GAME.url           Double-click shortcut to open in browser
├── data/
│   ├── rounds.json         Round definitions (answers, image paths, hints)
│   └── scores.json         Last-5 round history (auto-created, git-ignored)
├── static/
│   ├── css/style.css       Styles
│   ├── js/game.js          Frontend game logic
│   └── images/             Round images (20 JPEGs across 10 folders)
├── templates/
│   ├── index.html          Main menu
│   └── game.html           Game screen
└── scripts/
    └── download_images.py  Downloads images from Wikimedia Commons
```

---

## Extending the Game

To add more rounds:

1. Add a new entry to `data/rounds.json` following the existing schema.
2. Create the folder `static/images/round_NN/` and place two JPEGs inside
   named `image1.jpg` and `image2.jpg`.
3. That's it — the app picks rounds automatically.

---

## Rounds (v1)

| # | Answer     | Images               |
|---|------------|----------------------|
| 1 | sunflower  | sun + flower         |
| 2 | starfish   | star + fish          |
| 3 | eggplant   | egg + plant          |
| 4 | football   | foot + ball          |
| 5 | raincoat   | rain + coat          |
| 6 | firefly    | fire + fly           |
| 7 | teapot     | tea + pot            |
| 8 | snowball   | snow + ball          |
| 9 | butterfly  | butter + fly         |
|10 | doorbell   | door + bell          |

---

## License

Images downloaded by the script are from Wikimedia Commons and are used under
their respective free licenses (CC0, CC-BY, CC-BY-SA). The game code itself is
unlicensed — do whatever you like with it.
