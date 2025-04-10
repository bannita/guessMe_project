from flask import Blueprint, jsonify, request
from models import db, Word, User, GameStat, DailyLife, Guess
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

    session = GameSession.query.filter_by(user_id=user.id, date=today).first()
    # build today's hint from guesses (if session exists)
    hint = None
    if session:
        solution = session.word.word.lower()
        guesses = Guess.query.filter_by(game_session_id=session.id).all()

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

    return jsonify({
        "games_played": games_played,
        "wins": wins,
        "current_streak": current_streak,
        "max_streak": max_streak,
        "lives_left": lives_left,
        "hints_used": hints_used,
        "today_word": today_word,
        "hint": hint
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

    #if no lives row, give 5 lives
    if not lives:
        lives = DailyLife(user_id=user.id, date=today, lives_left=5)
        db.session.add(lives)
        db.session.commit()

    if lives.lives_left <= 0:
        return jsonify({"error": "No lives left to start a game"}), 403

    #subtract 1 life
    lives.lives_left -= 1
    db.session.commit()

    #get word IDs this user has already played
    #1) get all the word IDs the user has already played in previous games
    played_sessions = db.session.query(GameSession.word_id).filter_by(user_id=user.id).all()

    #2) convert list of tuples into list of integers
    used_word_ids = []
    for session in played_sessions:
        used_word_ids.append(session[0])


    #find words this user hasn't seen yet
    available_words = Word.query.filter(
        Word.is_solution == True,
        ~Word.id.in_(used_word_ids)
    ).all()

    if not available_words:
        return jsonify({"error": "No more words available for you!"}), 404

    #pick one random word
    chosen_word = random.choice(available_words)

    # Create a GameSession for today
    existing_session = GameSession.query.filter_by(user_id=user.id, date=today, active=True).first()
    if existing_session:
        existing_session.word_id = chosen_word.id
    else:
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
    data = request.get_json()
    email = data.get("email")
    guessed_word = data.get("guess")

    if not email or not guessed_word:
        return jsonify({"error": "Email and guess are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    today = date.today()

    # find the user's active GameSession for today
    session = GameSession.query.filter_by(user_id=user.id, date=today).first()
    if not session:
        return jsonify({"error": "No game session found for today"}), 404

    if not session.active:
        return jsonify({"message": "You've already completed today's game."}), 403

    word = session.word  # access the Word object via the session

    if not word:
        return jsonify({"error": "Game word not found"}), 404

    #clean and compare
    guess_clean = guessed_word.strip().lower()
    solution = word.word.lower()
    if guess_clean == solution:
        correct = True
    else:
        correct = False

    #save new guess in table
    new_guess = Guess(
    user_id=user.id,
    game_session_id=session.id,
    date=today,
    guess=guess_clean,
    correct=correct
    )

    # Wordle-style feedback logic
    feedback = []
    solution_letter_count = {}

    #count how many times each letter appears in the solution
    for letter in solution:
        if letter in solution_letter_count:
            solution_letter_count[letter] += 1
        else:
            solution_letter_count[letter] = 1

    #first pass: check for green (correct letter, correct position)
    for i in range(len(guess_clean)):
        if guess_clean[i] == solution[i]:
            feedback.append("green")
            solution_letter_count[guess_clean[i]] -= 1
        else:
            feedback.append(None)  # placeholder for now

    #second pass: check for yellow (wrong position) or gray (not in word)
    for i in range(len(guess_clean)):
        if feedback[i] is None:
            letter = guess_clean[i]
            if letter in solution_letter_count and solution_letter_count[letter] > 0:
                feedback[i] = "yellow"
                solution_letter_count[letter] -= 1
            else:
                feedback[i] = "gray"

    #track today's game stat
    game_stat = GameStat.query.filter_by(user_id=user.id, date=today).first()
    if not game_stat:
        game_stat = GameStat(user_id=user.id, date=today, attempts=0)
        db.session.add(game_stat)

    game_stat.attempts += 1

    if correct:
        game_stat.won = True
        session.active = False  #mark session as finished

    db.session.commit()

    return jsonify({
        "correct": correct,
        "your_guess": guessed_word,
        "solution_word": word.word if correct else None,
        "attempts": game_stat.attempts,
        "feedback": feedback
    })

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
    if not lives:
        lives = DailyLife(user_id=user.id, date=today, lives_left=5, hints_used=0)
        db.session.add(lives)
        db.session.commit()

    if lives.lives_left <= 0:
        return jsonify({"error": "No lives left to use a hint"}), 403

    #get current game session
    session = GameSession.query.filter_by(user_id=user.id, date=today, active=True).first()
    if not session:
        return jsonify({"error": "No active game session found"}), 404

    word = session.word
    if not word:
        return jsonify({"error": "Game word not found"}), 404

    solution = word.word.lower()

    #get guesses for this game session only
    guesses = Guess.query.filter_by(game_session_id=session.id).all()
    if not guesses:
        return jsonify({"error": "You must make at least one guess before using a hint"}), 403

    #build revealed state based on green matches
    revealed = []
    for i in range(len(solution)):
        revealed.append("_")

    for guess in guesses:
        guess_word = guess.guess.lower()
        for i in range(len(solution)):
            if i < len(guess_word) and guess_word[i] == solution[i]:
                revealed[i] = solution[i]  # mark green

    #reveal one unrevealed letter
    import random
    unrevealed_indices = []
    for i in range(len(solution)):
        if revealed[i] == "_":
            unrevealed_indices.append(i)

    if not unrevealed_indices:
        return jsonify({"message": "All letters already revealed!"}), 400

    hint_index = random.choice(unrevealed_indices)
    revealed[hint_index] = solution[hint_index]

    hint_string = " ".join(revealed)

    # Subtract life + track hint use
    lives.lives_left -= 1
    lives.hints_used += 1
    db.session.commit()

    return jsonify({
        "message": "Hint used (1 life spent)",
        "hint": hint_string,
        "lives_left": lives.lives_left,
        "hints_used": lives.hints_used
    })

