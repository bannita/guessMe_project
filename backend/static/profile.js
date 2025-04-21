const BASE_URL = "http://127.0.0.1:5000";

// When the page loads, fetch user info
window.addEventListener("DOMContentLoaded", async () => {
  try {
    const res = await fetch(`${BASE_URL}/api/me`, {
      credentials: "include"
    });

    const data = await res.json();

    if (data.email === "anibidzinashvili98@gmail.com") {
      const adminBtn = document.createElement("button");
      adminBtn.textContent = "🔧 Admin Panel";
      adminBtn.onclick = () => {
        window.location.href = "/admin";
      };
    
      document.querySelector(".card").appendChild(adminBtn);
    }

    if (res.ok) {
      document.getElementById("username").textContent = data.username;
      document.getElementById("email").textContent = data.email;
    } else {
      alert(data.error || "Failed to fetch user info.");
      window.location.href = "/index.html";
    }
  } catch (err) {
    alert("Server error.");
    console.error("Profile fetch error:", err);
    window.location.href = "/index.html";
  }
});

// Logout button
document.getElementById("logoutBtn").addEventListener("click", async () => {
  try {
    await fetch(`${BASE_URL}/api/logout`, {
      method: "POST",
      credentials: "include"
    });

    window.location.href = "/index.html";
  } catch (err) {
    alert("Logout failed.");
    console.error("Logout error:", err);
  }
});

// Delete account button
document.getElementById("deleteBtn").addEventListener("click", async () => {
  const confirmed = confirm("Are you sure you want to delete your account? This cannot be undone.");
  if (!confirmed) return;

  try {
    const res = await fetch(`${BASE_URL}/api/delete-account`, {
      method: "POST",
      credentials: "include"
    });

    const data = await res.json();

    if (res.ok) {
      alert("Your account has been deleted.");
      window.location.href = "/index.html";
    } else {
      alert(data.error || "Failed to delete account.");
    }
  } catch (err) {
    alert("Server error.");
    console.error("Delete account error:", err);
  }
});

// Back button
document.getElementById("backBtn").addEventListener("click", () => {
  window.history.back(); // or manually: window.location.href = "/game";
});

document.getElementById("changePasswordForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const currentPassword = document.getElementById("currentPassword").value;
  const newPassword = document.getElementById("newPassword").value;
  const msgBox = document.getElementById("passwordMsg");

  try {
    const res = await fetch(`${BASE_URL}/api/change-password`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword
      })
    });

    const data = await res.json();

    if (res.ok) {
      msgBox.textContent = data.message;
      msgBox.style.color = "green";
      document.getElementById("changePasswordForm").reset();
    } else {
      msgBox.textContent = data.error || "Failed to change password.";
      msgBox.style.color = "red";
    }

  } catch (err) {
    msgBox.textContent = "Server error.";
    msgBox.style.color = "red";
    console.error("Password change error:", err);
  }
});
