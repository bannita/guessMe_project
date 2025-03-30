import psycopg2
import json
from valid_words import it as valid_words_list  # Import the valid words list from the Python file

# Database connection details
DB_NAME = "guessme_db"
DB_USER = "postgres"
DB_PASSWORD = "4260abk"  # Use the password you set for PostgreSQL
DB_HOST = "localhost"
DB_PORT = "5432"

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
)
cur = conn.cursor()

# 1️⃣ Import Valid Words from valid_words.py
print("Importing valid words...")
for word in valid_words_list:
    word = word.strip().lower()
    if len(word) == 5:  # Ensure only 5-letter words
        try:
            cur.execute(
                "INSERT INTO words (word, is_solution) VALUES (%s, FALSE) ON CONFLICT (word) DO NOTHING;",
                (word,),
            )
        except Exception as e:
            print(f"Error inserting valid word {word}: {e}")

# 2️⃣ Import Solution Words from solution_words.json
print("Importing solution words...")
with open("solution_words.json", "r") as file:
    solution_words = json.load(file)

for word in solution_words:
    word = word.strip().lower()
    if len(word) == 5:  # Ensure only 5-letter words
        try:
            cur.execute(
                "INSERT INTO words (word, is_solution) VALUES (%s, TRUE) ON CONFLICT (word) DO NOTHING;",
                (word,),
            )
        except Exception as e:
            print(f"Error inserting solution word {word}: {e}")

# Commit changes and close connection
conn.commit()
cur.close()
conn.close()

print("✅ Words imported successfully!")
