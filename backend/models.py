#Defines database tables: User, Word, GameStat, DailyLife, etc.
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

#user's table
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # hashed later
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
class Word(db.Model):
    __tablename__ = 'words'

    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(5), unique=True, nullable=False)
    is_solution = db.Column(db.Boolean, nullable=False, default=False)
    used = db.Column(db.Boolean, nullable=False, default=False)