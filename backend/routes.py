from flask import Blueprint, jsonify, request
from models import db, Word, User, GameStat
import random
from werkzeug.security import generate_password_hash, check_password_hash


routes = Blueprint("routes", __name__)

#get random unused work for game
@routes.route("/api/random-word")
def random_word():
    unused_words = Word.query.filter_by(is_solution=True, used=False).all()
    if not unused_words:
        return jsonify({"error": "No unused words available"}), 404
    chosen = random.choice(unused_words)
    return jsonify({"word": chosen.word})

#mark word as used
@routes.route("/api/use-word/<word>")
def use_word(word):
    w = Word.query.filter_by(word=word).first()
    if not w:
        return jsonify({"error": "Word not found"}), 404
    w.used = True
    db.session.commit()
    return jsonify({"message": f"Word '{word}' marked as used."})

#check validity of word
@routes.route("/api/check-word/<guess>")
def check_word(guess):
    w = Word.query.filter_by(word=guess.lower()).first()
    return jsonify({
        "word": guess,
        "valid": bool(w),
        "is_solution": w.is_solution if w else False
    })

#user stats
@routes.route("/api/stats/<email>")
def stats(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    games = GameStat.query.filter_by(user_id=user.id).all()
    games_played = len(games)
    
    #count games won
    wins = 0
    for g in games:
        if g.won:
            wins += 1

    return jsonify({
        "games_played": games_played,
        "wins": wins,
        "win_streak": 0,  #will add streak logic later
        "lives_left": 5,  #placeholder for lives system
        "hints_used": 0   #placeholder for hint system
    })

#signup route
@routes.route("/api/signup", methods = ['POST'])
def signup():
    data = request.get_json()
    
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    #check if user already exists
    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        return jsonify({"error": "Username or email already in use"}), 409

    #create new user
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Signup successful!"}), 201


@routes.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    #find user by email
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "User not found"}), 404
    
    #check password
    if not check_password_hash(user.password, password):
        return jsonify({"error": "Incorrect password"}), 401

    return jsonify({"message": "Login successful!"}), 200


@routes.route("/api/end-game", methods=["POST"])
def end_game():
    data = request.get_json()

    email = data.get("email")
    won = data.get("won")
    attempts = data.get("attempts")

    if not email or won is None or attempts is None:
        return jsonify({"error": "Missing game data"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    game = GameStat(
        user_id=user.id,
        won=bool(won),
        attempts=int(attempts)
    )
    db.session.add(game)
    db.session.commit()

    return jsonify({"message": "Game result recorded"}), 201