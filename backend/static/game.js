//Sends/receives guesses, shows hints, updates lives.
const BASE_URL = "http://127.0.0.1:5000";
const NUM_ROWS = 6;
const WORD_LENGTH = 5;

let currentRow = 0;
let currentCol = 0;
let guesses = Array.from({ length: NUM_ROWS }, () => Array(WORD_LENGTH).fill(""));

const grid = document.getElementById("guessGrid");
const keyboard = document.getElementById("keyboard");
const message = document.getElementById("message");
const livesDisplay = document.getElementById("lives");
const hintBtn = document.getElementById("hintBtn");

// === Start Game ===
async function startGame() {
  try {
    const res = await fetch(`${BASE_URL}/api/start-game`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({}) // We no longer send email
    });

    const data = await res.json();

    if (res.ok) {
      livesDisplay.textContent = `Lives: ${data.lives_left}`;
      console.log("Game started:", data.word);
    } else {
      showMessage(data.error || "Failed to start game");
    }
  } catch (err) {
    console.error("Error starting game:", err);
    showMessage("Server error");
  }
}
startGame();

// === Create Grid & Keyboard ===
function createGrid() {
  for (let row = 0; row < NUM_ROWS; row++) {
    for (let col = 0; col < WORD_LENGTH; col++) {
      const tile = document.createElement("div");
      tile.classList.add("tile");
      tile.id = `tile-${row}-${col}`;
      grid.appendChild(tile);
    }
  }
}
createGrid();

const keys = [..."QWERTYUIOP", ..."ASDFGHJKL", "Enter", ..."ZXCVBNM", "←"];
function createKeyboard() {
  keys.forEach(key => {
    const keyBtn = document.createElement("button");
    keyBtn.textContent = key;
    keyBtn.classList.add("key");
    keyBtn.addEventListener("click", () => handleKeyPress(key));
    keyboard.appendChild(keyBtn);
  });
}
createKeyboard();

// === Input Handling ===
function handleKeyPress(key) {
  if (key === "←") {
    deleteLetter();
  } else if (key === "Enter") {
    submitGuess();
  } else if (/^[A-Z]$/.test(key)) {
    addLetter(key);
  }
}

function addLetter(letter) {
  if (currentCol < WORD_LENGTH) {
    guesses[currentRow][currentCol] = letter;
    const tile = document.getElementById(`tile-${currentRow}-${currentCol}`);
    tile.textContent = letter;
    tile.classList.add("filled");
    currentCol++;
  }
}

function deleteLetter() {
  if (currentCol > 0) {
    currentCol--;
    guesses[currentRow][currentCol] = "";
    const tile = document.getElementById(`tile-${currentRow}-${currentCol}`);
    tile.textContent = "";
    tile.classList.remove("filled");
  }
}

// === Submit Guess ===
async function submitGuess() {
  const guessWord = guesses[currentRow].join("");

  if (guessWord.length < WORD_LENGTH) {
    showMessage("Not enough letters");
    return;
  }

  try {
    const res = await fetch(`${BASE_URL}/api/guess`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ guess: guessWord }) // No email
    });

    const data = await res.json();

    if (res.ok) {
      updateTileFeedback(data.feedback);
      currentRow++;
      currentCol = 0;

      if (data.correct) {
        showMessage("🎉 Correct!");
      } else if (currentRow === NUM_ROWS) {
        showMessage("😢 Out of guesses!");
      }
    } else {
      showMessage(data.error || "Invalid guess");
    }
  } catch (err) {
    console.error("Guess error:", err);
    showMessage("Server error");
  }
}

// === Update Feedback Colors ===
function updateTileFeedback(feedback) {
  for (let i = 0; i < WORD_LENGTH; i++) {
    const tile = document.getElementById(`tile-${currentRow}-${i}`);
    tile.classList.add(feedback[i]); // 'green', 'yellow', 'gray'
  }
}

// === Use Hint ===
hintBtn.addEventListener("click", async () => {
  try {
    const res = await fetch(`${BASE_URL}/api/use-hint`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({})
    });

    const data = await res.json();

    if (res.ok) {
      livesDisplay.textContent = `Lives: ${data.lives_left}`;
      showMessage(`Hint: ${data.hint}`);
    } else {
      showMessage(data.error || "No hints available");
    }
  } catch (err) {
    console.error("Hint error:", err);
    showMessage("Server error");
  }
});

// === Show Message ===
function showMessage(text) {
  message.textContent = text;
  setTimeout(() => {
    message.textContent = "";
  }, 2500);
}
