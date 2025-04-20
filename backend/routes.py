from flask import Blueprint, jsonify, request, session
from models import db, Word, User, GameStat, DailyLife, Guess, GameSession
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

    # sort games by date or ID (you already do this)
    games_sorted = sorted(games, key=lambda g: g.id)

    # Calculate max streak
    max_streak = 0
    temp_streak = 0
    for game in games_sorted:
        if game.won:
            temp_streak += 1
            max_streak = max(max_streak, temp_streak)
        else:
            temp_streak = 0

    # Calculate current streak (wins in a row from most recent game backwards)
    current_streak = 0
    for game in reversed(games_sorted):
        if game.won:
            current_streak += 1
        else:
            break  # streak is broken


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

    # get today's chosen word from this user's game session
    today_word = None
    #game_session = GameSession.query.filter_by(user_id=user.id, date=today).first()
    game_session = GameSession.query.filter_by(user_id=user.id, date=today).order_by(GameSession.id.desc()).first()

    if game_session and game_session.word:
        today_word = game_session.word.word

    # build today's hint from guesses (if session exists)
    hint = None
    if game_session:
        solution = game_session.word.word.lower()
        guesses = Guess.query.filter_by(game_session_id=game_session.id).all()

        if guesses:
            revealed = []
            for i in range(len(solution)):
                revealed.append("_")

            for guess in guesses:
                guess_word = guess.guess.lower()
                for i in range(len(solution)):
                    if i < len(guess_word) and guess_word[i] == solution[i]:
                        revealed[i] = solution[i]

            hint = " ".join(revealed)

    attempts = 0
    if game_session:
        attempts = Guess.query.filter_by(game_session_id=game_session.id).count()

    return jsonify({
        "games_played": games_played,
        "wins": wins,
        "current_streak": current_streak,
        "max_streak": max_streak,
        "lives_left": lives_left,
        "hints_used": hints_used,
        "today_word": today_word,
        "hint": hint,
        "attempts": attempts,
    })

#check validity of email
def is_valid_email(email):
    is_valid = False
    
    if "@" in email and "." in email:
        if email.index("@") < email.index(".") and email.index("@") > 0 and email.index(".") < (len(email)-1):
            is_valid = True

    return is_valid

#signup route
@routes.route("/api/signup", methods = ['POST'])
def signup():
    data = request.get_json()
    
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400
    
    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        return jsonify({"error": "Username or email already in use"}), 409

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    session.permanent = True
    session["email"] = new_user.email

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
    
    session.permanent = True
    session["email"] = user.email

    return jsonify({"message": "Login successful!"}), 200

#logout route
@routes.route("/api/logout", methods=["POST"])
def logout():
    session.clear()  #clears everything from session
    return jsonify({"message": "You have been logged out."}), 200

@routes.route("/api/me", methods=["GET"])
def me():
    email = session.get("email")

    if not email:
        return jsonify({"error": "Not logged in"}), 401

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "email": user.email,
        "username": user.username,
        "date_joined": user.date_joined.strftime("%Y-%m-%d")
    }), 200

#route for deleting account
@routes.route("/api/delete-account", methods=["POST"])
def delete_account():
    email = session.get("email")

    if not email:
        return jsonify({"error": "You must be logged in to delete your account"}), 401

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    #delete user related data from tables
    GameStat.query.filter_by(user_id=user.id).delete()
    GameSession.query.filter_by(user_id=user.id).delete()
    Guess.query.filter_by(user_id=user.id).delete()
    DailyLife.query.filter_by(user_id=user.id).delete()

    #delete the user account
    db.session.delete(user)
    db.session.commit()

    #clear session
    session.clear()

    return jsonify({"message": "Your account has been deleted."}), 200

#end_game route
@routes.route("/api/end-game", methods=["POST"])
def end_game():
    email = session.get("email")
    if not email:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    won = data.get("won")
    attempts = data.get("attempts")

    if won is None or attempts is None:
        return jsonify({"error": "Missing game data"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    today = date.today()

    game = GameStat.query.filter_by(user_id=user.id, date=today).order_by(GameStat.id.desc()).first()
    if game:
        game.won = bool(won)
        game.attempts = int(attempts)
    else:
        game = GameStat(user_id=user.id, date=today, won=bool(won), attempts=int(attempts))

    db.session.commit()

    # mark the active session as done
    today = date.today()
    session_to_close = GameSession.query.filter_by(user_id=user.id, date=today, active=True).first()
    if session_to_close:
        session_to_close.active = False
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
    email = session.get("email")
    if not email:
        return jsonify({"error": "Not logged in"}), 401

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

#start the game
@routes.route("/api/start-game", methods=["POST"])
def start_game():
    email = session.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    today = date.today()
    lives = DailyLife.query.filter_by(user_id=user.id, date=today).first()

    #if no lives row, give 5 lives
    if not lives:
        lives = DailyLife(user_id=user.id, date=today, lives_left=5)
        db.session.add(lives)
        db.session.commit()

    lives = DailyLife.query.filter_by(user_id=user.id, date=today).first()

    if lives.lives_left <= 0:
        return jsonify({"error": "No lives left to start a game", "lives_left": lives.lives_left}), 403


    #subtract 1 life
    lives.lives_left -= 1
    db.session.commit()

    #get word IDs this user has already played
    #1) get all the word IDs the user has already played in previous games
    played_sessions = db.session.query(GameSession.word_id).filter_by(user_id=user.id).all()

    #2) convert list of tuples into list of integers
    used_word_ids = []
    for gamesession in played_sessions:
        used_word_ids.append(gamesession[0])


    #find words this user hasn't seen yet
    available_words = Word.query.filter(
        Word.is_solution == True,
        ~Word.id.in_(used_word_ids)
    ).all()

    if not available_words:
        return jsonify({"error": "No more words available for you!"}), 404

    #pick one random word
    chosen_word = random.choice(available_words)

   # Mark all previous sessions as inactive
    GameSession.query.filter_by(user_id=user.id, date=today).update({"active": False})

    # Always create a new session when starting a game
    new_session = GameSession(user_id=user.id, word_id=chosen_word.id, date=today)
    db.session.add(new_session)

    db.session.commit()

    return jsonify({
        "message": "Game started",
        "word": chosen_word.word,
        "lives_left": lives.lives_left
    })


@routes.route("/api/guess", methods=["POST"])
def guess():
    email = session.get("email")
    if not email:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    guessed_word = data.get("guess")

    if not guessed_word:
        return jsonify({"error": "Guess is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    today = date.today()

    # find the user's active GameSession for today
    game_session = GameSession.query.filter_by(user_id=user.id, date=today, active=True).first()

    if not game_session:
        return jsonify({"error": "No active game session found for today"}), 403

    word = game_session.word  # access the Word object via the session

    if not word:
        return jsonify({"error": "Game word not found"}), 404

    # Clean and compare
    guess_clean = guessed_word.strip().lower()
    solution = word.word.lower()

    # Check if guess exists in word table
    valid_word = Word.query.filter_by(word=guess_clean).first()
    if not valid_word:
        return jsonify({"error": "Invalid guess: word not in dictionary"}), 400

    correct = guess_clean == solution

    # Save the guess
    new_guess = Guess(
        user_id=user.id,
        game_session_id=game_session.id,
        date=today,
        guess=guess_clean,
        correct=correct
    )
    db.session.add(new_guess)

    # Feedback logic (Wordle-style)
    feedback = []
    solution_letter_count = {}

    for letter in solution:
        solution_letter_count[letter] = solution_letter_count.get(letter, 0) + 1

    # First pass: green letters
    for i in range(len(guess_clean)):
        if guess_clean[i] == solution[i]:
            feedback.append("green")
            solution_letter_count[guess_clean[i]] -= 1
        else:
            feedback.append(None)

    # Second pass: yellow or gray
    for i in range(len(guess_clean)):
        if feedback[i] is None:
            letter = guess_clean[i]
            if letter in solution_letter_count and solution_letter_count[letter] > 0:
                feedback[i] = "yellow"
                solution_letter_count[letter] -= 1
            else:
                feedback[i] = "gray"

    # Update game stats
    game_stat = GameStat.query.filter_by(user_id=user.id, date=today).first()
    if not game_stat:
        game_stat = GameStat(user_id=user.id, date=today, attempts=0)
        db.session.add(game_stat)

    game_stat.attempts += 1

    if correct:
        game_stat.won = True
        game_session.active = False

    db.session.commit()

    return jsonify({
        "correct": correct,
        "your_guess": guessed_word,
        "solution_word": word.word,
        "attempts": game_stat.attempts,
        "feedback": feedback
    })


@routes.route("/api/use-hint", methods=["POST"])
def use_hint():
    email = session.get("email")

    if not email:
        return jsonify({"error": "Not logged in"}), 401

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    today = date.today()

    lives = DailyLife.query.filter_by(user_id=user.id, date=today).first()
    if not lives:
        lives = DailyLife(user_id=user.id, date=today, lives_left=5, hints_used=0)
        db.session.add(lives)
        db.session.commit()

    if lives.lives_left <= 0:
        return jsonify({"error": "No lives left to use a hint"}), 403

    # get current game session
    game_session = GameSession.query.filter_by(user_id=user.id, date=today, active=True).first()
    if not game_session:
        return jsonify({"error": "No active game session found"}), 404

    word = game_session.word
    if not word:
        return jsonify({"error": "Game word not found"}), 404

    solution = word.word.lower()

    # get guesses for this game session only
    guesses = Guess.query.filter_by(game_session_id=game_session.id).all()
    if not guesses:
        return jsonify({"error": "You must make at least one guess before using a hint"}), 403

    # build revealed state based on green matches
    revealed = ["_"] * len(solution)

    for guess in guesses:
        guess_word = guess.guess.lower()
        for i in range(len(solution)):
            if i < len(guess_word) and guess_word[i] == solution[i]:
                revealed[i] = solution[i]  # mark green

    # reveal one unrevealed letter
    import random
    unrevealed_indices = [i for i, char in enumerate(revealed) if char == "_"]

    if not unrevealed_indices:
        return jsonify({"message": "All letters already revealed!"}), 400

    hint_index = random.choice(unrevealed_indices)
    revealed[hint_index] = solution[hint_index]

    hint_string = " ".join(revealed)

    # subtract life + track hint use
    lives.lives_left -= 1
    lives.hints_used += 1
    db.session.commit()

    return jsonify({
        "message": "Hint used (1 life spent)",
        "hint": hint_string,
        "lives_left": lives.lives_left,
        "hints_used": lives.hints_used
    })

@routes.route("/api/stats/me")
def stats_me():
    email = session.get("email")
    if not email:
        return jsonify({"error": "Not logged in"}), 401

    return stats(email)  # use your existing stats function



