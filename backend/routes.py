from flask import Blueprint, jsonify, request, session
from models import db, Word, User, GameStat, DailyLife, Guess, GameSession
import random
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

# Common status codes we use(I need this comment for me to remamber status codes so everyone else can ignore it^-^)
# 200: OK (success)
# 201: Created
# 400: Bad request (e.g. missing fields)
# 401: Unauthorized (not logged in)
# 403: Forbidden (logged in but not allowed)
# 404: Not Found (user/word/game not found)
# 409: Conflict (duplicate signup)

routes = Blueprint("routes", __name__)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ AUTHENTICATION ROUTES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

    existing_user = User.query.filter( (User.username == username) | (User.email == email)).first()
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

    #deletes guesses first (they depend on game_sessions)
    Guess.query.filter_by(user_id=user.id).delete()
    
    #deletse sessions and other stats
    GameStat.query.filter_by(user_id=user.id).delete()
    GameSession.query.filter_by(user_id=user.id).delete()
    DailyLife.query.filter_by(user_id=user.id).delete()

    #finally deletes the user
    db.session.delete(user)
    db.session.commit()

    session.clear()

    return jsonify({"message": "Your account has been deleted."}), 200

@routes.route("/api/change-password", methods=["POST"])
def change_password():
    email = session.get("email")
    if not email:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    current_pw = data.get("current_password")
    new_pw = data.get("new_password")

    if not current_pw or not new_pw:
        return jsonify({"error": "Both current and new passwords are required."}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Check current password
    if not check_password_hash(user.password, current_pw):
        return jsonify({"error": "Current password is incorrect."}), 403

    # Update password
    user.password = generate_password_hash(new_pw)
    db.session.commit()

    return jsonify({"message": "Password changed successfully."}), 200


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GAME ROUTES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

    #if no lives row for today, give 5 lives
    if not lives:
        lives = DailyLife(user_id=user.id, date=today, lives_left=5)
        db.session.add(lives)
        db.session.commit()

    lives = DailyLife.query.filter_by(user_id=user.id, date=today).first()

    if lives.lives_left <= 0:
        return jsonify({"error": "No lives left to start a game", "lives_left": lives.lives_left}), 403

    db.session.commit()

    #get word IDs this user has already played

    #get all the word IDs the user has already played in previous games
    played_sessions = db.session.query(GameSession.word_id).filter_by(user_id=user.id).all()

    #convert list of tuples into list of integers
    used_word_ids = []
    for gamesession in played_sessions:
        used_word_ids.append(gamesession[0])


    #find words this user hasnt seen yet
    available_words = Word.query.filter(Word.is_solution == True, ~Word.id.in_(used_word_ids)).all()

    if not available_words:
        return jsonify({"error": "No more words available for you!"}), 404

    #pick one random word from available ones
    chosen_word = random.choice(available_words)

    #mark all previous sessions for the uer inactive
    GameSession.query.filter_by(user_id=user.id, date=today).update({"active": False})

    #always create a new session when starting a game
    new_session = GameSession(user_id=user.id, word_id=chosen_word.id, date=today)
    db.session.add(new_session)

    db.session.commit()

    return jsonify({
        "message": "Game started",
        "word": chosen_word.word,
        "lives_left": lives.lives_left
    })

#guess route
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

    #find active GameSession
    game_session = GameSession.query.filter_by(user_id=user.id, date=today, active=True).first()
    if not game_session:
        return jsonify({"error": "No active game session found for today"}), 403

    word = game_session.word
    if not word:
        return jsonify({"error": "Game word not found"}), 404

    #clean and compare
    guess_clean = guessed_word.strip().lower()
    solution = word.word.lower()

    #check if guess exists in words table
    valid_word = Word.query.filter_by(word=guess_clean).first()
    if not valid_word:
        return jsonify({"error": "Invalid guess: word not in dictionary"}), 400

    correct = guess_clean == solution

    #save guess
    new_guess = Guess(
        user_id=user.id,
        game_session_id=game_session.id,
        date=today,
        guess=guess_clean,
        correct=correct
    )
    db.session.add(new_guess)

    #feedback logic (green/yellow/gray)
    feedback = []
    solution_letter_count = {}

    for letter in solution:
        if letter in solution_letter_count:
            solution_letter_count[letter] += 1
        else:
            solution_letter_count[letter] = 1

    for i in range(len(guess_clean)):
        if guess_clean[i] == solution[i]:
            feedback.append("green")
            solution_letter_count[guess_clean[i]] -= 1
        else:
            feedback.append(None)

    for i in range(len(guess_clean)):
        if feedback[i] is None:
            letter = guess_clean[i]
            if letter in solution_letter_count and solution_letter_count[letter] > 0:
                feedback[i] = "yellow"
                solution_letter_count[letter] -= 1
            else:
                feedback[i] = "gray"

    db.session.commit()

    return jsonify({
        "correct": correct,
        "your_guess": guessed_word,
        "solution_word": word.word,
        "feedback": feedback
    })

@routes.route("/api/end-game", methods=["POST"])
def end_game():
    email = session.get("email")
    if not email:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    won = data.get("won")

    if won is None:
        return jsonify({"error": "Missing game result (won)"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    today = date.today()

    #find active game session
    session_to_close = GameSession.query.filter_by(user_id=user.id, date=today, active=True).first()
    if not session_to_close:
        return jsonify({"error": "No active game session"}), 400

    #count guesses made in this session
    attempts = Guess.query.filter_by(game_session_id=session_to_close.id).count()

    #create a new GameStat always
    new_stat = GameStat(
        user_id=user.id,
        date=today,
        won=bool(won),
        attempts=attempts
    )
    db.session.add(new_stat)

    #close the session
    session_to_close.active = False

    #subtract a life
    lives = DailyLife.query.filter_by(user_id=user.id, date=today).first()
    if lives and lives.lives_left > 0:
        lives.lives_left -= 1

    db.session.commit()
    return jsonify({"message": "Game result recorded"}), 201


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ LIVES AND HINTS ROUTES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

    #get current game session
    game_session = GameSession.query.filter_by(user_id=user.id, date=today, active=True).first()
    if not game_session:
        return jsonify({"error": "No active game session found"}), 404

    word = game_session.word
    if not word:
        return jsonify({"error": "Game word not found"}), 404

    solution = word.word.lower()

    #get guesses for this game session only
    guesses = Guess.query.filter_by(game_session_id=game_session.id).all()
    if not guesses:
        return jsonify({"error": "You must make at least one guess before using a hint"}), 403

    #build revealed state based on green matches
    revealed = ["_"] * len(solution)

    for guess in guesses:
        guess_word = guess.guess.lower()
        for i in range(len(solution)):
            if i < len(guess_word) and guess_word[i] == solution[i]:
                revealed[i] = solution[i]

    #reveal one unrevealed letter
    import random
    unrevealed_indices = []

    for i in range(len(revealed)):
        if revealed[i] == "_":
            unrevealed_indices.append(i)

    if not unrevealed_indices:
        return jsonify({"message": "All letters already revealed!"}), 400

    hint_index = random.choice(unrevealed_indices)
    revealed[hint_index] = solution[hint_index]

    hint_string = " ".join(revealed)

    #subtract life and track hint use
    lives.lives_left -= 1
    lives.hints_used += 1
    db.session.commit()

    return jsonify({
        "message": "Hint used (1 life spent)",
        "hint": hint_string,
        "lives_left": lives.lives_left,
        "hints_used": lives.hints_used
    })

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ STATS ROUTES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@routes.route("/api/stats/<email>")
def stats(email):
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    today = date.today()

    all_game_stats = GameStat.query.filter_by(user_id=user.id).order_by(GameStat.id.asc()).all()
    games_played = len(all_game_stats)

    wins = 0
    current_streak = 0
    max_streak = 0
    temp_streak = 0

    for game in all_game_stats:
        if game.won:
            wins += 1
            temp_streak += 1
            if temp_streak > max_streak:
                max_streak = temp_streak
        else:
            temp_streak = 0

    current_streak = temp_streak

    lives_today = DailyLife.query.filter_by(user_id=user.id, date=today).first()
    if lives_today:
        lives_left = lives_today.lives_left
        hints_used = lives_today.hints_used
    else:
        lives_left = 0
        hints_used = 0

    #gets today's latest word
    today_session = GameSession.query.filter_by(user_id=user.id, date=today).order_by(GameSession.id.desc()).first()
    if today_session and today_session.word:
        today_word = today_session.word.word
    else:
        today_word = None

    #today's attempts
    attempts = 0
    if today_session:
        attempts = Guess.query.filter_by(game_session_id=today_session.id).count()

    if games_played > 0:
        win_percentage = wins/games_played*100
    else:
        win_percentage = 0

    return jsonify({
        "games_played": games_played,
        "wins": wins,
        "current_streak": current_streak,
        "max_streak": max_streak,
        "lives_left": lives_left,
        "hints_used": hints_used,
        "today_word": today_word,
        "attempts": attempts,
        "win_percentage": win_percentage
    })

@routes.route("/api/stats/me")
def stats_me():
    email = session.get("email")
    if not email:
        return jsonify({"error": "Not logged in"}), 401

    return stats(email) #uses existing stats function

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ADMIN ROUTES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@routes.route("/api/admin/users", methods=["GET"])
def admin_get_users():
    email = session.get("email")
    if email != "anibidzinashvili98@gmail.com":
        return jsonify({"error": "Unauthorized"}), 403

    users = User.query.all()
    user_list = []
    for user in users:
        user_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "date_joined": user.date_joined.strftime("%Y-%m-%d")
        })

    return jsonify(user_list), 200

@routes.route("/api/admin/delete-user/<int:user_id>", methods=["DELETE"])
def admin_delete_user(user_id):
    email = session.get("email")
    if email != "anibidzinashvili98@gmail.com":
        return jsonify({"error": "Unauthorized"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    #cllean up user's related data
    Guess.query.filter_by(user_id=user.id).delete()
    GameSession.query.filter_by(user_id=user.id).delete()
    GameStat.query.filter_by(user_id=user.id).delete()
    DailyLife.query.filter_by(user_id=user.id).delete()

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": f"User {user.username} deleted."}), 200

@routes.route("/api/admin/words", methods=["GET"])
def admin_get_words():
    email = session.get("email")
    if email != "anibidzinashvili98@gmail.com":
        return jsonify({"error": "Unauthorized"}), 403

    words = Word.query.all()
    word_list = []
    for word in words:
        word_list.append({
            "id": word.id,
            "word": word.word,
            "is_solution": word.is_solution,
            "used": word.used
        })

    return jsonify(word_list), 200

@routes.route("/api/admin/add-word", methods=["POST"])
def admin_add_word():
    email = session.get("email")
    if email != "anibidzinashvili98@gmail.com":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    word_text = data.get("word", "").strip().lower()
    is_solution = data.get("is_solution", False)

    if not word_text:
        return jsonify({"error": "Word is required"}), 400

    #check if word already exists
    existing = Word.query.filter_by(word=word_text).first()
    if existing:
        return jsonify({"error": "Word already exists"}), 409

    new_word = Word(
        word=word_text,
        is_solution=is_solution,
        used=False
    )
    db.session.add(new_word)
    db.session.commit()

    return jsonify({"message": f"Word '{word_text}' added."}), 201

@routes.route("/api/admin/delete-word/<int:word_id>", methods=["DELETE"])
def admin_delete_word(word_id):
    email = session.get("email")
    if email != "anibidzinashvili98@gmail.com":
        return jsonify({"error": "Unauthorized"}), 403

    word = Word.query.get(word_id)
    if not word:
        return jsonify({"error": "Word not found"}), 404

    db.session.delete(word)
    db.session.commit()

    return jsonify({"message": f"Word '{word.word}' deleted."}), 200







