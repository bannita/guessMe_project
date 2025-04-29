from flask import Flask, session, redirect
from flask_sqlalchemy import SQLAlchemy
import os
from routes import routes
from models import db, User, Word, GameStat, DailyLife, GameSession, Guess
from datetime import timedelta

app = Flask(__name__, static_url_path="")

app.secret_key = os.getenv("SECRET_KEY", "fallbacksecretkey")
app.register_blueprint(routes)

app.permanent_session_lifetime = timedelta(days=60)

# Environment-based DB config
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  #instead of creating a new SQLAlchemy(app)

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




#this will now properly use the models
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
