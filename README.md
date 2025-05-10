# Guess Me - A Word Guessing Game Web App

**Author:** Ani Bidzinashvili  
**Course:** CS 250, Final Project  
**Repository:** https://github.com/bannita/guessMe_project/tree/main  

---

## Project Description

**Guess Me** is a web-based word game inspired by Wordle. Players log in, guess 5-letter words, and try to find the correct one using letter-by-letter feedback. The app tracks played games, wins, win rate, streaks, lives, hints, and more. It includes a custom-built admin panel for managing users and word entries.

---

## Features

* User Authentication: Sign up, log in, and log out.
* Daily Word Challenge: A new 5-letter word to guess each day.
* Lives System: Players have 5 lives per day; incorrect guesses and hints consume lives.
* Hint Mechanism: Reveal one letter of the word at the cost of one life.
* Color-Coded Feedback: Visual indicators for correct letters and positions (Green -> correct letter, correct position; Yellow -> correct letter, wrong position).
* Player Statistics:
    * Games played and won
    * Win rate, current streak and max streak
    * Lives and hints, attempts needed/correct word if game was lost
* Personal Profile Page: View personal information, change password and delete account.
* Admin Panel:
    * Manage user accounts
    * Add, edit, or remove words
* Fully containerized using Docker and PostgreSQL


---

## Tech Stack

* Frontend: HTML, CSS, JavaScript
* Backend: Python, Flask, Flask-SQLAlchemy
* Database: PostgreSQL
* Tools: Docker, VS Code, DBeaver

---
## 🚀 Deployment Instructions

This project uses **Docker Compose** to run the entire application — including the Flask backend and PostgreSQL database — in isolated containers. No manual setup of Python, PostgreSQL, or dependencies is required.

### ✅ Prerequisites

Before starting, make sure you have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

---

### 🛠️ Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/bannita/guessMe_project.git
   cd guessMe_project
   ```

2. **Set up environment variables:**

   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

   Then open `.env` and fill in your values:
   ```
   DB_NAME=guessme_db
   DB_USER=your_postgres_username
   DB_PASSWORD=your_postgres_password
   DB_HOST=db
   DB_PORT=5432
   SECRET_KEY=your_flask_secret_key
   ```

---

### ▶️ Running the Application

To build and start the app with Docker Compose:

```bash
docker-compose up --build
```

This command will:

- Start the PostgreSQL database container
- Build and start the Flask web app
- Make the app accessible at:  
  👉 [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

### 📦 (One-Time) Import Word Lists

If the word database is empty (e.g. on first setup), run this command to import valid and solution words:

```bash
docker-compose exec web python -m setup_scripts.import_words
```

This reads from `valid_words.py` and `solution_words.json` and populates the database.

---

### 🛑 Stopping the App

To stop the app but keep data:
```bash
docker-compose down
```

To stop and **delete all data** (⚠️ includes users and word lists):
```bash
docker-compose down --volumes
```


## How to Run the App (using Docker)

### 1. Clone the repository

```bash
git clone https://github.com/bannita/guessMe_project.git
cd guessMe_project
```

### 2. Set up environment variables

Copy the `.env.example` file:

```bash
cp .env.example .env
```

Then fill in the actual values (e.g. your database password).

### 3. Run using Docker Compose

```bash
docker build -t guessme_app .
docker run -p 5000:5000 --name guessme_container --env-file .env guessme_app
```

* The app will run at: `http://localhost:5000`
* PostgreSQL will run in the background on port `5432`

---

## Environment Variables (from `.env`)

| Variable      | Description                                          |
| ------------- | ---------------------------------------------------- |
| `DB_NAME`     | PostgreSQL database name                             |
| `DB_USER`     | PostgreSQL username                                  |
| `DB_PASSWORD` | PostgreSQL password                                  |
| `DB_HOST`     | host.docker.internal                                 |
| `DB_PORT`     | Usually `5432`                                       |
| `SECRET_KEY`  | Flask secret key for sessions                        |

---

## How to Use/Test the App

1. Go to `http://localhost:5000`
2. Create an account or log in
3. Start a game
4. Enter 5-letter guesses (max 6 tries)
5. Use hints if needed (each hint costs 1 life)
6. View your stats and streaks after each game
7. Visit your profile to update password or delete account

---

### Game Rules & Feedback Logic

- Each guess must be a valid 5-letter word.
- The game provides feedback using Wordle-style colors:
  - **Green**: Letter is correct and in the correct position.
  - **Yellow**: Letter is correct but in the wrong position.
  - **Gray**: Letter is not in the word at all.
- You have **6 attempts per game**.
- You start with **5 lives per day**:
  - 1 life is lost per game.
  - 1 life is lost per hint used.
  - Lives reset at midnight.

  ---

## Admin Panel Access

To access the admin panel:

* Use the email `anibidzinashvili98@gmail.com` when logging in (password: guessme)
* Once logged in, an "Admin Panel" button will appear on your profile page

Admin capabilities:

* View and delete users
* View, add, or delete words

---

## Resetting the Word List (optional)

If you need to re-import solution or valid words:

```bash
python setup_scripts/import_words.py
```

This script uses SQLAlchemy and pulls from:

* `setup_scripts/solution_words.json`
* `setup_scripts/valid_words.py`

---

## API Endpoints Overview

### Authentication

| Method | Route              | Description                          |
|--------|--------------------|--------------------------------------|
| POST   | `/api/signup`      | Register a new user                  |
| POST   | `/api/login`       | Log in with email and password       |
| POST   | `/api/logout`      | Log out the current session          |
| GET    | `/api/me`          | Get current logged-in user's info    |

---

### Profile Management

| Method | Route                   | Description                          |
|--------|-------------------------|--------------------------------------|
| POST   | `/api/delete-account`   | Permanently delete current user      |
| POST   | `/api/change-password`  | Change current user's password       |

---

### Game Logic

| Method | Route              | Description                                  |
|--------|--------------------|----------------------------------------------|
| POST   | `/api/start-game`  | Start a new game session (if lives left)     |
| POST   | `/api/guess`       | Submit a word guess                          |
| POST   | `/api/end-game`    | End the current game (win/loss & save stats) |

---

### Lives & Hints

| Method | Route             | Description                                   |
|--------|-------------------|-----------------------------------------------|
| POST   | `/api/use-hint`   | Reveal one unrevealed letter (costs 1 life)   |

---

### Stats

| Method | Route                   | Description                                      |
|--------|-------------------------|--------------------------------------------------|
| GET    | `/api/stats/me`         | Get stats for current logged-in user            |
| GET    | `/api/stats/<email>`    | Get stats for a specific user (by email)        |

---

### Admin Panel (restricted to admin email)

| Method | Route                                  | Description                             |
|--------|----------------------------------------|-----------------------------------------|
| GET    | `/api/admin/users`                     | View all users                          |
| DELETE | `/api/admin/delete-user/<user_id>`     | Delete a user by ID                     |
| GET    | `/api/admin/words`                     | View all words                          |
| POST   | `/api/admin/add-word`                  | Add a new word                          |
| DELETE | `/api/admin/delete-word/<word_id>`     | Delete a word by ID                     |


---

## Project Structure

```
backend/
└── app.py           → Main Flask app
├── models.py        → SQLAlchemy models
├── routes.py        → All game/auth/admin API routes
├── static/          → HTML, CSS, JS files
setup_scripts/
├── import_words.py  → Word loader script
.env.example         → Safe env template
Dockerfile / docker-compose.yml
requirements.txt     → Python dependencies
```
### Frontend Files Overview

```
static/
├── index.html       → Landing page with login/signup form
├── index.css        → Styles for landing page
├── auth.js          → Handles login and signup form submissions

├── game.html        → Main game interface
├── game.css         → Styles for the game page
├── game.js          → Handles game logic, guesses, hints, and feedback

├── stats.html       → Stats and replay screen
├── stats.css        → Styles for stats page
├── stats.js         → Displays win/loss, streaks, and stats

├── profile.html     → User profile page
├── profile.css      → Styles for profile page
├── profile.js       → Change password and delete account logic

├── admin.html       → Admin panel interface
├── admin.css        → Styles for admin panel
├── admin.js         → View/delete users and add/delete words
```

---

## Screenshots

### Authentication
<img src="https://github.com/user-attachments/assets/6b21d6fa-c82d-48f1-8145-70a0687c159e" width="500"/>

### Game
<img src="https://github.com/user-attachments/assets/4e313a2f-e3b5-4c7d-ae67-c72261a51e7c" width="500"/>

### Stats
<img src="https://github.com/user-attachments/assets/2aab2eec-23cf-4267-9353-1b8a15cfbebf" width="500"/>

### Profile
<img src="https://github.com/user-attachments/assets/345808e7-a161-481a-a34a-0fe6c974f4fc" width="500"/>

### Admin Panel
<img src="https://github.com/user-attachments/assets/d1526915-4d2b-4f51-99a6-6a3446354a4d" width="500"/>

---


## Thank You

This app was built with care as a final project for CS250 and was inspired by Wordle and other guessing games.  
I hope you enjoy exploring it! 


---