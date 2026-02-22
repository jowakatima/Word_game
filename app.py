import json
import os
import random
from datetime import datetime, timezone

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "word-game-dev-secret-2026")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ROUNDS_FILE = os.path.join(DATA_DIR, "rounds.json")
SCORES_FILE = os.path.join(DATA_DIR, "scores.json")

MAX_HISTORY = 5
MAX_WRONG = 4
HINT_AFTER = 2  # reveal hint after this many wrong guesses


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def load_rounds():
    with open(ROUNDS_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_scores():
    if not os.path.exists(SCORES_FILE):
        return {"history": []}
    with open(SCORES_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_scores(scores_data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(scores_data, f, indent=2)


def get_round_by_id(rounds, round_id):
    return next((r for r in rounds if r["id"] == round_id), None)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    scores = load_scores()
    history = scores.get("history", [])
    # Show newest first, max 5
    history_display = list(reversed(history[-MAX_HISTORY:]))
    return render_template("index.html", history=history_display)


@app.route("/game")
def game():
    rounds = load_rounds()
    completed = session.get("completed_rounds", [])

    # Select a round not yet played this session
    available = [r for r in rounds if r["id"] not in completed]
    if not available:
        # All rounds done — reset and start fresh
        session["completed_rounds"] = []
        available = rounds

    chosen = random.choice(available)

    session["round_id"] = chosen["id"]
    session["wrong_count"] = 0
    session["hint_shown"] = False

    return render_template("game.html", round=chosen, total_rounds=len(rounds))


@app.route("/api/answer", methods=["POST"])
def check_answer():
    data = request.get_json(silent=True) or {}
    guess = data.get("guess", "").strip().lower()

    rounds = load_rounds()
    round_id = session.get("round_id")
    current = get_round_by_id(rounds, round_id)

    if not current:
        return jsonify({"error": "No active round"}), 400

    correct = current["answer"].lower()
    wrong_count = session.get("wrong_count", 0)

    # Correct answer
    if guess == correct:
        return jsonify({
            "result": "correct",
            "answer": current["answer"],
            "wrong_count": wrong_count,
        })

    # Wrong answer
    wrong_count += 1
    session["wrong_count"] = wrong_count

    hint_text = None
    show_hint = False

    if wrong_count >= HINT_AFTER:
        show_hint = True
        hint_text = current["hint"]
        session["hint_shown"] = True

    # Loss condition
    if wrong_count >= MAX_WRONG:
        return jsonify({
            "result": "loss",
            "answer": current["answer"],
            "wrong_count": wrong_count,
            "hint": hint_text,
            "show_hint": show_hint,
        })

    return jsonify({
        "result": "wrong",
        "wrong_count": wrong_count,
        "show_hint": show_hint,
        "hint": hint_text,
        "guesses_remaining": MAX_WRONG - wrong_count,
    })


@app.route("/api/end", methods=["POST"])
def end_round():
    data = request.get_json(silent=True) or {}
    result = data.get("result")  # "win" or "loss"

    round_id = session.get("round_id")
    wrong_count = session.get("wrong_count", 0)

    rounds = load_rounds()
    current = get_round_by_id(rounds, round_id)

    entry = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "round_id": round_id,
        "answer": current["answer"] if current else "unknown",
        "result": result,
        "wrong_guesses": wrong_count,
    }

    scores = load_scores()
    scores["history"].append(entry)
    scores["history"] = scores["history"][-MAX_HISTORY:]
    save_scores(scores)

    # Mark round as completed in session
    completed = session.get("completed_rounds", [])
    if round_id and round_id not in completed:
        completed.append(round_id)
    session["completed_rounds"] = completed

    return jsonify({"redirect": url_for("index")})


@app.route("/api/next", methods=["POST"])
def next_round():
    return jsonify({"redirect": url_for("game")})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
