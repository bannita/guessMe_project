from flask import Blueprint, jsonify
from models import db, Word
import random

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
@routes.route("/api/stats")
def stats():
    return jsonify({
        "games_played": 0,
        "wins": 0,
        "win_streak": 0,
        "lives_left": 5,
        "hints_used": 0
    })