const BASE_URL = "http://127.0.0.1:5000";

window.addEventListener("DOMContentLoaded", async () => {
  await loadUsers();
  await loadWords();

  //handle new word submission
  document.getElementById("addWordForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const word = document.getElementById("newWord").value.trim().toLowerCase();
    const isSolution = document.getElementById("isSolution").checked;

    if (!word) return alert("Please enter a word!");

    try {
      const res = await fetch(`${BASE_URL}/api/admin/add-word`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ word, is_solution: isSolution })
      });

      const data = await res.json();

      if (res.ok) {
        alert(data.message);
        document.getElementById("addWordForm").reset();
        await loadWords();
      } else {
        alert(data.error || "Failed to add word.");
      }
    } catch (err) {
      console.error("Add word error:", err);
      alert("Server error while adding word.");
    }
  });
});

//load all users
async function loadUsers() {
  try {
    const res = await fetch(`${BASE_URL}/api/admin/users`, { credentials: "include" });
    const users = await res.json();

    const userList = document.getElementById("userList");
    userList.innerHTML = "";

    users.forEach(user => {
      const li = document.createElement("li");
      li.textContent = `${user.username} (${user.email}) `;

      const delBtn = document.createElement("button");
      delBtn.textContent = "Delete";
      delBtn.onclick = () => deleteUser(user.id, user.username);

      li.appendChild(delBtn);
      userList.appendChild(li);
    });
  } catch (err) {
    console.error("Failed to load users:", err);
  }
}

//delete user
async function deleteUser(id, username) {
  if (!confirm(`Delete user '${username}'?`)) return;

  try {
    const res = await fetch(`${BASE_URL}/api/admin/delete-user/${id}`, {
      method: "DELETE",
      credentials: "include"
    });

    const data = await res.json();

    if (res.ok) {
      alert(data.message);
      await loadUsers();
    } else {
      alert(data.error || "Failed to delete user.");
    }
  } catch (err) {
    console.error("Delete user error:", err);
    alert("Server error while deleting user.");
  }
}

//load all words
async function loadWords() {
  try {
    const res = await fetch(`${BASE_URL}/api/admin/words`, { credentials: "include" });
    const words = await res.json();

    const wordList = document.getElementById("wordList");
    wordList.innerHTML = "";

    words.forEach(word => {
      const li = document.createElement("li");
      li.textContent = `${word.word} (Solution: ${word.is_solution}, Used: ${word.used}) `;

      const delBtn = document.createElement("button");
      delBtn.textContent = "Delete";
      delBtn.onclick = () => deleteWord(word.id, word.word);

      li.appendChild(delBtn);
      wordList.appendChild(li);
    });
  } catch (err) {
    console.error("Failed to load words:", err);
  }
}

//delete a word
async function deleteWord(id, wordText) {
  if (!confirm(`Delete word '${wordText}'?`)) return;

  try {
    const res = await fetch(`${BASE_URL}/api/admin/delete-word/${id}`, {
      method: "DELETE",
      credentials: "include"
    });

    const data = await res.json();

    if (res.ok) {
      alert(data.message);
      await loadWords();
    } else {
      alert(data.error || "Failed to delete word.");
    }
  } catch (err) {
    console.error("Delete word error:", err);
    alert("Server error while deleting word.");
  }
}
