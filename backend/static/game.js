const BASE_URL = "http://127.0.0.1:5000";
const NUM_ROWS = 6;
const WORD_LENGTH = 5;

let currentRow = 0;
let currentCol = 0;
let guesses = [];

for (let i = 0; i < NUM_ROWS; i++) {
  let row = [];
  for (let j = 0; j < WORD_LENGTH; j++) {
    row.push("");
  }
  guesses.push(row);
}

const grid = document.getElementById("guessGrid");
const message = document.getElementById("message");
const livesDisplay = document.getElementById("lives");
const hintBtn = document.getElementById("hintBtn");
const tracker = document.getElementById("letter-tracker");
const alphabet = "abcdefghijklmnopqrstuvwxyz";

for (let letter of alphabet) {
  const box = document.createElement("div");
  box.classList.add("letter-box");
  box.id = `letter-${letter}`;
  box.textContent = letter;
  tracker.appendChild(box);
}

//start Game
async function startGame() {
  try {
    const res = await fetch(`${BASE_URL}/api/start-game`, {
      method: "POST",
      credentials: "include",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({})
    });

    const data = await res.json();
    console.log("Lives received:", data.lives_left);

    if (res.ok) {
      livesDisplay.textContent = `Lives: ${data.lives_left}`;
      console.log("Game started:", data.word);
    } else {
      //if lives are 0 show noLivesContainer
      if (data.lives_left !== undefined) {
        livesDisplay.textContent = `Lives: ${data.lives_left}`;

        if (data.lives_left <= 0) {
          document.getElementById("noLivesContainer").classList.remove("hidden");
          document.getElementById("guessGrid").style.display = "none";
          document.getElementById("keyboard")?.remove();
          document.getElementById("letter-tracker").style.display = "none";
          hintBtn.style.display = "none";
        }
      }

      showMessage(data.error || "Failed to start game");
    }
  } catch (err) {
    console.error("Error starting game:", err);
    showMessage("Server error");
  }
}
startGame();


//creates 5x6 wordle grid
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

//listens for real keyboard input
document.addEventListener("keydown", (e) => {
  const key = e.key;

  if (key === "Enter") {
    submitGuess();
  } else if (key === "Backspace") {
    deleteLetter();
  } else if (/^[a-zA-Z]$/.test(key)) {
    addLetter(key.toUpperCase());
  }
});

//letter handling
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

//submit a new guess
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
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ guess: guessWord })
    });

    const data = await res.json();

    if (res.ok) {
      updateTileFeedback(data.feedback);

      data.feedback.forEach((status, index) => {
        const letter = guessWord[index].toLowerCase();
        const box = document.getElementById(`letter-${letter}`);
      
        if (!box) return;
      
        if (status === "green") {
          box.classList.remove("gray", "yellow");
          box.classList.add("green");
        } else if (status === "yellow" && !box.classList.contains("green")) {
          box.classList.remove("gray");
          box.classList.add("yellow");
        } else if (
          status === "gray" &&
          !box.classList.contains("green") &&
          !box.classList.contains("yellow")
        ) {
          box.classList.add("gray");
        }
      });

      
      currentRow++;
      currentCol = 0;
    
      if (data.correct) {
        message.textContent = "🎉 Congratulations! You guessed it!";
        message.className = "message win";
        await endGame(true); //record win

        setTimeout(() => {
          window.location.href = "/stats";
        }, 1000); //delay to show message briefly

      } else if (currentRow === NUM_ROWS) {
        message.textContent = `😢 You lost! The correct word was: ${data.solution_word}`;
        message.className = "message lose";
        await endGame(false); //record loss

        setTimeout(() => {
          window.location.href = "/stats";
        }, 2500); //slightly longer delay for dramatic effect lol
      }
    } else {
      showMessage(data.error || "Invalid guess");
    }
  } catch (err) {
    console.error("Guess error:", err);
    showMessage("Server error");
  }
}

//update feedback colors
function updateTileFeedback(feedback) {
  for (let i = 0; i < WORD_LENGTH; i++) {
    const tile = document.getElementById(`tile-${currentRow}-${i}`);
    tile.classList.add(feedback[i]); // 'green', 'yellow', 'gray'
  }
}

//use hint
hintBtn.addEventListener("click", async () => {
  try {
    const res = await fetch(`${BASE_URL}/api/use-hint`, {
      method: "POST",
      credentials: "include",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({})
    });

    const data = await res.json();

    if (res.ok) {
      livesDisplay.textContent = `Lives: ${data.lives_left}`;
      if (data.lives_left <= 0) {
        hintBtn.disabled = true;
        hintBtn.style.opacity = "0.5";
        hintBtn.title = "You're out of lives, You cannot request more hints!";
      }
      document.getElementById("hint").textContent = `Hint: ${data.hint}`;
    } else {
      //update lives if backend still returns lives_left in error response
      if (data.lives_left !== undefined) {
        livesDisplay.textContent = `Lives: ${data.lives_left}`;
      }
      showMessage(data.error || "No hints available");
    }
    
  } catch (err) {
    console.error("Hint error:", err);
    showMessage("Server error");
  }
});

//show message
function showMessage(text) {
  message.textContent = text;
  setTimeout(() => {
    message.textContent = "";
  }, 3500);
}

async function endGame(won) {
  try {
    await fetch(`${BASE_URL}/api/end-game`, {
      method: "POST",
      credentials: "include",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ won })
    });
  } catch (err) {
    console.error("Failed to record game result:", err);
  }
}

document.getElementById("logoutBtn").addEventListener("click", async () => {
  try {
    await fetch(`${BASE_URL}/api/logout`, {
      method: "POST",
      credentials: "include"
    });
    
    setTimeout(() => {
      window.location.href = "/index.html";
    }, 300); //wait 300ms to let cookie clear and then redirect to login/signup page
  } catch (err) {
    console.error("Logout failed:", err);
  }
});

document.getElementById("profileBtn").addEventListener("click", () => {
  window.location.href = "/profile";
});

document.getElementById("goToStatsBtn").addEventListener("click", () => {
  window.location.href = "/stats";
});