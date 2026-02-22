"use strict";

// ---------------------------------------------------------------------------
// Element references
// ---------------------------------------------------------------------------
const guessForm    = document.getElementById("guess-form");
const guessInput   = document.getElementById("guess-input");
const guessBtn     = document.getElementById("guess-btn");
const wrongCount   = document.getElementById("wrong-count");
const hintBox      = document.getElementById("hint-box");
const hintText     = document.getElementById("hint-text");
const feedbackMsg  = document.getElementById("feedback-msg");
const overlay      = document.getElementById("result-overlay");
const resultIcon   = document.getElementById("result-icon");
const resultTitle  = document.getElementById("result-title");
const resultAnswer = document.getElementById("result-answer");
const btnNext      = document.getElementById("btn-next");
const btnMenu      = document.getElementById("btn-menu");

let roundEnded = false;

// ---------------------------------------------------------------------------
// Form submission
// ---------------------------------------------------------------------------
guessForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (roundEnded) return;

  const guess = guessInput.value.trim();
  if (!guess) return;

  guessBtn.disabled = true;

  try {
    const res = await fetch("/api/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ guess }),
    });
    const data = await res.json();
    handleResponse(data);
  } catch (err) {
    showFeedback("Network error — please try again.", "error");
    guessBtn.disabled = false;
  }
});

// ---------------------------------------------------------------------------
// Response handler
// ---------------------------------------------------------------------------
function handleResponse(data) {
  wrongCount.textContent = data.wrong_count ?? wrongCount.textContent;

  if (data.result === "correct") {
    roundEnded = true;
    disableGuessForm();
    showResultOverlay("win", data.answer, data.wrong_count);
    saveResult("win");

  } else if (data.result === "loss") {
    roundEnded = true;
    disableGuessForm();
    if (data.show_hint && data.hint) showHint(data.hint);
    showResultOverlay("loss", data.answer, data.wrong_count);
    saveResult("loss");

  } else {
    // Wrong but still playing
    if (data.show_hint && data.hint) {
      showHint(data.hint);
    }
    const remaining = data.guesses_remaining ?? 0;
    showFeedback(
      `Not quite! ${remaining} guess${remaining === 1 ? "" : "es"} remaining.`,
      "wrong"
    );
    guessInput.value = "";
    guessBtn.disabled = false;
    guessInput.focus();
  }
}

// ---------------------------------------------------------------------------
// UI helpers
// ---------------------------------------------------------------------------
function showHint(text) {
  hintText.textContent = text;
  hintBox.classList.remove("hidden");
}

function showFeedback(text, type) {
  feedbackMsg.textContent = text;
  feedbackMsg.className = `feedback feedback--${type}`;
  feedbackMsg.classList.remove("hidden");
}

function disableGuessForm() {
  guessInput.disabled = true;
  guessBtn.disabled = true;
}

function showResultOverlay(result, answer, wrongGuesses) {
  if (result === "win") {
    resultIcon.textContent = "✓";
    resultIcon.className = "result-icon result-icon--win";
    resultTitle.textContent = "You got it!";
    resultTitle.className = "result-title result-title--win";
  } else {
    resultIcon.textContent = "✗";
    resultIcon.className = "result-icon result-icon--loss";
    resultTitle.textContent = "Better luck next time!";
    resultTitle.className = "result-title result-title--loss";
  }

  const guessLabel = wrongGuesses === 1 ? "1 wrong guess" : `${wrongGuesses} wrong guesses`;
  resultAnswer.textContent = `The answer was: ${answer}  (${guessLabel})`;

  overlay.classList.remove("hidden");
}

// ---------------------------------------------------------------------------
// Round end — persist score
// ---------------------------------------------------------------------------
async function saveResult(result) {
  try {
    await fetch("/api/end", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ result }),
    });
  } catch (err) {
    // Score save failed silently — game still navigates normally
    console.warn("Score save failed:", err);
  }
}

// ---------------------------------------------------------------------------
// Overlay buttons
// ---------------------------------------------------------------------------
btnNext.addEventListener("click", async () => {
  btnNext.disabled = true;
  try {
    const res = await fetch("/api/next", { method: "POST" });
    const data = await res.json();
    window.location.href = data.redirect;
  } catch {
    window.location.href = "/game";
  }
});

btnMenu.addEventListener("click", () => {
  window.location.href = "/";
});
