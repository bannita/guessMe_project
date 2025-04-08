from flask import Blueprint, jsonify, request
from models import db, Word, User, GameStat, DailyLife
import random
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

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
    for game in games:
        if game.won:
            wins += 1

    #calculate win streak
    current_streak = 0
    max_streak = 0
    temp_streak = 0

    #calculate max streak
    for game in games:
        if game.won:
            temp_streak += 1
            if temp_streak > max_streak:
                max_streak = temp_streak
        else:
            temp_streak = 0

    #check if the streak is still going
    current_streak = 0
    if len(games) > 0:
        last_game = games[len(games) - 1]
        if last_game.won:
            current_streak = temp_streak

    #get lives for today
    today = date.today()
    lives_left = 0
    lives = DailyLife.query.filter_by(user_id=user.id, date=today).first()
    #if row for lives exists today we assign number of lives left
    if lives:
        lives_left = lives.lives_left

    #get hints used for today
    if lives:
        hints_used = lives.hints_used
    else:
        hints_used = 0
    
    #get today's chosen word
    used_words = Word.query.filter_by(is_solution=True, used=True).all()

    if len(used_words) > 0:
        last_used_word = used_words[len(used_words) - 1]
        today_word = last_used_word.word
    else:
        today_word = None

            
    return jsonify({
        "games_played": games_played,
        "wins": wins,
        "current_streak": current_streak,
        "max_streak": max_streak,
        "lives_left": lives_left,
        "hints_used": hints_used,
        "today_word": today_word
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

#login route
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

#end_game route
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

#route for giving lives
@routes.route("/api/lives/<email>")
def get_lives(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    today = date.today()

    #check if lives already recorded for today
    lives = DailyLife.query.filter_by(user_id=user.id, date=today).first()

    if not lives:
        #create new entry for today
        lives = DailyLife(user_id=user.id, lives_left=5, date=today)
        db.session.add(lives)
        db.session.commit()

    return jsonify({
        "date": today.strftime("%Y-%m-%d"),
        "lives_left": lives.lives_left
    })

#route for substracting live
@routes.route("/api/use-life", methods=["POST"])
def use_life():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    today = date.today()
    lives = DailyLife.query.filter_by(user_id=user.id, date=today).first()

    #if no record exists for today create one with 5 lives
    if not lives:
        lives = DailyLife(user_id=user.id, lives_left=5, date = today)
        db.session.add(lives)
        db.session.commit()

    if lives.lives_left <= 0:
        return jsonify({"error": "No lives left for today"}), 403

    #subtract one life
    lives.lives_left -= 1
    db.session.commit()

    return jsonify({
        "message": "Life used",
        "lives_left": lives.lives_left
    })

#route for using hint
@routes.route("/api/use-hint", methods=["POST"])
def use_hint():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    today = date.today()
    lives = DailyLife.query.filter_by(user_id=user.id, date=today).first()

    #if no row for today, create one with 5 lives
    if not lives:
        lives = DailyLife(user_id=user.id, date=today, lives_left=5)
        db.session.add(lives)
        db.session.commit()

    if lives.lives_left <= 0:
        return jsonify({"error": "No lives left for hint"}), 403

    # Subtract a life
    lives.lives_left -= 1
    lives.hints_used += 1
    db.session.commit()

    return jsonify({
        "message": "Hint used, 1 life subtracted",
        "lives_left": lives.lives_left
        "hints_used": lives.hints_used,
    })

#start the game
@routes.route("/api/start-game", methods=["POST"])
def start_game():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    today = date.today()
    lives = DailyLife.query.filter_by(user_id=user.id, date=today).first()

    #if no lives row exists, give 5 lives
    if not lives:
        lives = DailyLife(user_id=user.id, date=today, lives_left=5)
        db.session.add(lives)
        db.session.commit()

    if lives.lives_left <= 0:
        return jsonify({"error": "No lives left to start a game"}), 403

    #subtract 1 life for starting the game
    lives.lives_left -= 1
    db.session.commit()

    #get a random unused solution word
    words = Word.query.filter_by(is_solution=True, used=False).all()
    if not words:
        return jsonify({"error": "No unused solution words available"}), 404

    chosen_word = random.choice(words)
    #mark word as used
    chosen_word.used = True
    db.session.commit()

    return jsonify({
        "message": "Game started",
        "word": chosen_word.word,
        "lives_left": lives.lives_left
    })
