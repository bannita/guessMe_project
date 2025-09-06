from flask import Flask, session, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from backend.routes import routes
from backend.models import db, User, Word, GameStat, DailyLife, GameSession, Guess
from datetime import timedelta
from flask_cors import CORS

# creates flask app and allow static files to be served directly from the root URL
app = Flask(__name__, static_url_path="")

# secrets / sessions
app.secret_key = os.getenv("SECRET_KEY", "fallbacksecretkey")
app.permanent_session_lifetime = timedelta(days=60)

# (optional) safer cookies for production (Render uses HTTPS)
# You can leave these on locally too; they won't break local dev.
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
# set Secure cookies if you're on HTTPS (Render custom domain / onrender.com is HTTPS)
app.config["SESSION_COOKIE_SECURE"] = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"


# attach API routes
app.register_blueprint(routes)

# ----- Database config -----
# Prefer a single DATABASE_URL (Render), else fall back to separate DB_* vars (local)
db_url = os.getenv("DATABASE_URL")

if db_url:
    # Normalize deprecated scheme for SQLAlchemy/psycopg2
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
else:
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# connect models to this app
db.init_app(app)

# ---- Static pages routing ----
@app.route("/")
def serve_home():
    email = session.get("email")
    if not email or email == "null":
        return app.send_static_file("index.html")
    return redirect("/game")

@app.route("/game")
def serve_game():
    if not session.get("email"):
        return redirect("/")
    return app.send_static_file("game.html")

@app.route("/stats")
def serve_stats():
    if "email" not in session:
        return redirect("/")
    return app.send_static_file("stats.html")

@app.route("/profile")
def serve_profile():
    if "email" not in session:
        return redirect("/")
    return app.send_static_file("profile.html")

@app.route("/admin")
def serve_admin():
    email = session.get("email")
    admin_email = os.getenv("ADMIN_EMAIL", "anibidzinashvili98@gmail.com")
    if email != admin_email:
        return redirect("/")
    return app.send_static_file("admin.html")

# health check for platforms
@app.get("/health")
def health():
    return "ok", 200

# auto-create tables (safe to keep; it's idempotent)
with app.app_context():
    db.create_all()

# Don't run app.run() here; Gunicorn will import 'app' from this module.
# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)

'''
from flask import Flask, session, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from backend.routes import routes
from backend.models import db, User, Word, GameStat, DailyLife, GameSession, Guess
from datetime import timedelta
from flask_cors import CORS


#creates flask app and allow static files to be served directly from the root URL
app = Flask(__name__, static_url_path="")

app.secret_key = os.getenv("SECRET_KEY", "fallbacksecretkey")

#attaches API routes from routes.py to the main app
app.register_blueprint(routes)

app.permanent_session_lifetime = timedelta(days=60)

#loads database connection settings from environment variables
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

#sets database connection string for SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = (f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#connects database models to this specific flask app
db.init_app(app)

@app.route("/")
def serve_home():
    email = session.get("email")
    if not email or email == "null":
        return app.send_static_file("index.html")
    return redirect("/game")

@app.route("/game")
def serve_game():
    if not session.get("email"):
        return redirect("/")
    return app.send_static_file("game.html")

@app.route("/stats")
def serve_stats():
    if "email" not in session:
        return redirect("/")
    return app.send_static_file("stats.html")

@app.route("/profile")
def serve_profile():
    if "email" not in session:
        return redirect("/")
    return app.send_static_file("profile.html")

@app.route("/admin")
def serve_admin():
    email = session.get("email")
    if email != "anibidzinashvili98@gmail.com":
        return redirect("/")
    return app.send_static_file("admin.html")

#tells SQLAlchemy to create all tables in database based on model classes
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
'''
