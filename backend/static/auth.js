//Sends login/signup data to backend (/login, /signup).

// Base URL of the Flask backend
const BASE_URL = "http://127.0.0.1:5000";

// Login function
async function login() {
  const email = document.getElementById("login-email").value;
  const password = document.getElementById("login-password").value;
  const errorBox = document.getElementById("login-error");

  try {
    const response = await fetch(`${BASE_URL}/api/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password })
    });

    const data = await response.json();

    if (response.ok) {
      // ✅ redirect to game page after session sets
      setTimeout(() => {
        window.location.href = "/game";
      }, 300);
    } else {
      errorBox.innerText = data.error || "Login failed.";
    }
  } catch (err) {
    errorBox.innerText = "Server error.";
  }
}

// Signup function
async function signup() {
  const username = document.getElementById("signup-username").value;
  const email = document.getElementById("signup-email").value;
  const password = document.getElementById("signup-password").value;
  const errorBox = document.getElementById("signup-error");

  try {
    const response = await fetch(`${BASE_URL}/api/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ username, email, password })
    });

    const data = await response.json();

    if (response.ok) {
      console.log("✅ Signup success! Redirecting now...");
      window.location.replace("/game");
    } else {
      errorBox.innerText = data.error || "Signup failed.";
    }
  } catch (err) {
    errorBox.innerText = "Server error.";
  }
}
