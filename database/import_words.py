import psycopg2
import json
from valid_words import it as valid_words_list  #import valid words list from python file
import os

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

#connect to postgreSQL
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

#import valid words (is_solution = FALSE, used = FALSE)
for word in valid_words_list:
    word = word.strip().lower()
    if len(word) == 5:
        cur.execute(
            """
            INSERT INTO words (word, is_solution, used)
            VALUES (%s, FALSE, FALSE)
            ON CONFLICT (word) DO NOTHING;
            """,
            (word,)
        )

#import solution words (is_solution = TRUE, used = FALSE)
with open("database/solution_words.json", "r") as file:
    solution_words = json.load(file)

for word in solution_words:
    word = word.strip().lower()
    if len(word) == 5:
        cur.execute(
            """
            INSERT INTO words (word, is_solution, used)
            VALUES (%s, TRUE, FALSE)
            ON CONFLICT (word)
            DO UPDATE SET is_solution = TRUE;
            """,
            (word,)
        )

conn.commit()
cur.close()
conn.close()