#Defines database tables: User, Word, GameStat, DailyLife, etc.
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

#user's table
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)  # hashed later
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
class Word(db.Model):
    __tablename__ = 'words'

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(5), unique=True, nullable=False)
    is_solution = db.Column(db.Boolean, nullable=False, default=False)
    used = db.Column(db.Boolean, nullable=False, default=False)

class GameStat(db.Model):
    __tablename__ = 'game_stats'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    won = db.Column(db.Boolean, default=False)
    attempts = db.Column(db.Integer, default=0)

    user = relationship("User", backref="game_stats")

class DailyLife(db.Model):
    __tablename__ = 'daily_life'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    lives_left = db.Column(db.Integer, default=5)
    hints_used = db.Column(db.Integer, default=0)

    user = relationship("User", backref="daily_life")

class GameSession(db.Model):
    __tablename__ = 'game_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    active = db.Column(db.Boolean, default=True)  #helps track if session is still ongoing

    user = db.relationship("User", backref="game_sessions")
    word = db.relationship("Word")

class Guess(db.Model):
    __tablename__ = 'guesses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_session_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False)
    date = db.Column(db.Date, default=date.today)
    guess = db.Column(db.String(5), nullable=False)
    correct = db.Column(db.Boolean, default=False)

    user = db.relationship("User", backref="guesses")
    session = db.relationship("GameSession", backref="guesses")