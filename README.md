# Guess Me - A Word Guessing Game Web App

**Author:** Ani Bidzinashvili
**Course:** \[CS 250, Final Project]

---

## Project Description

**Guess Me** is a web-based word game inspired by Wordle. Players log in, guess 5-letter words, and try to find the correct one using letter-by-letter feedback. The app tracks played games, wins, win rate, streaks, lives, hints, and more. It includes a custom-built admin panel for managing users and word entries.

---

## Features

* User authentication (signup, login, logout)
* 5-letter word guessing game with color-coded feedback
* Daily lives system (5 lives per day)
* Hint system that reveals one letter per hint (costs 1 life)
* Game statistics tracking: playd games, wins, win rate, attempts, streaks, lives used
* Personal profile page with personal info and features to change password and account delete
* Admin panel: add/delete words, manage users
* Fully containerized using Docker and PostgreSQL

---

## Tech Stack

* Frontend: HTML, CSS, JavaScript
* Backend: Python, Flask, Flask-SQLAlchemy
* Database: PostgreSQL
* Tools: Docker, VS Code, DBeaver

---

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
| `DB_HOST`     | host.docker.internal                                |
| `DB_PORT`     | Usually `5432`                                       |
| `SECRET_KEY`  | Flask secret key for sessions                        |

---

## How to Use the App

1. Go to `http://localhost:5000`
2. Create an account or log in
3. Start a game
4. Enter 5-letter guesses (max 6 tries)
5. Use hints if needed (each hint costs 1 life)
6. View your stats and streaks after each game
7. Visit your profile to update password or delete account

---

## Admin Panel Access

To access the admin panel:

* Use the email `anibidzinashvili98@gmail.com` when signing up
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

## Acknowledgments

* Built as a final project for \[CS250]
* Inspired by Wordle and other guessing games

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

---

## Good Luck and Have Fun

Thanks for reviewing the project.
Feel free to open issues, try new guesses, or suggest improvements.

---
