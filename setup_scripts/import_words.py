import json
import os
from backend.models import db, Word
from valid_words import it as valid_words_list
from flask import Flask
from backend.app import app

with app.app_context():
    print("Importing valid words...")

    for word in valid_words_list:
        word = word.strip().lower()
        if len(word) == 5:
            existing = Word.query.filter_by(word=word).first()
            if not existing:
                new_word = Word(word=word, is_solution=False, used=False)
                db.session.add(new_word)

    print("Importing solution words...")

    with open("setup_scripts/solution_words.json", "r") as file:
        solution_words = json.load(file)

    for word in solution_words:
        word = word.strip().lower()
        if len(word) == 5:
            existing = Word.query.filter_by(word=word).first()
            if existing:
                existing.is_solution = True
            else:
                new_word = Word(word=word, is_solution=True, used=False)
                db.session.add(new_word)

    db.session.commit()
    print("Import complete.")