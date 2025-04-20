//Fetches and shows user stats from /stats route.

const BASE_URL = "http://127.0.0.1:5000";

// Run when the page loads
window.addEventListener("DOMContentLoaded", async () => {
  try {
    const res = await fetch(`${BASE_URL}/api/stats/me`, {
      credentials: "include"
    });

    const data = await res.json();

    if (!res.ok) {
      document.body.innerHTML = "<h1>Error: Please log in again.</h1>";
      return;
    }

    // Show game result
    const resultEl = document.getElementById("result");
    if (data.today_word && data.current_streak > 0) {
      resultEl.textContent = "🎉 You won!";
      document.getElementById("attemptsRow").textContent = `You guessed the word in ${data.attempts} tries.`;
      
    } else {
      resultEl.textContent = "😢 You lost!";
      document.getElementById("correctWordRow").textContent =
        `The correct word was: ${data.today_word}`;
    }

    // Fill in stats
    document.getElementById("gamesPlayed").textContent = data.games_played;
    document.getElementById("wins").textContent = data.wins;
    document.getElementById("currentStreak").textContent = data.current_streak;
    document.getElementById("maxStreak").textContent = data.max_streak;
    document.getElementById("livesLeft").textContent = data.lives_left;
    document.getElementById("hintsUsed").textContent = data.hints_used;

    // Decide whether to show replay or "no lives" message
    const replayBtn = document.getElementById("replayBtn");
    const noLivesMsg = document.getElementById("noLivesMsg");

    if (data.lives_left > 0) {
      replayBtn.style.display = "inline-block";
      noLivesMsg.style.display = "none";

      replayBtn.addEventListener("click", () => {
        window.location.href = "/game";
      });
    } else {
      replayBtn.style.display = "none";
      noLivesMsg.textContent = "💔 No more lives left. Come back tomorrow!";
    }

  } catch (err) {
    console.error("Error loading stats:", err);
    document.body.innerHTML = "<h1>Something went wrong loading your stats.</h1>";
  }
});
