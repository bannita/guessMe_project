from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from routes import routes
from models import db, User, Word, GameStat, DailyLife

app = Flask(__name__)
app.register_blueprint(routes)

# Environment-based DB config
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  #instead of creating a new SQLAlchemy(app)

@app.route("/")
def home():
    return "<h1>hi kitty ^-^</h1>"

#this will now properly use the models
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
