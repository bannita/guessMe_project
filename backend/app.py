#Starts the Flask app and registers routes from other files.
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

app.config['SQLALCHEMY_DATABASE_URI'] = ( f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route("/")
def home():
    return " hi kitty ^-^"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)