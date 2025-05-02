import sqlite3
import os
import subprocess

conn = sqlite3.connect("flashcards.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS flashcards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_pl TEXT NOT NULL,
    word_en TEXT NOT NULL,
    set_id INTEGER NOT NULL,
    FOREIGN KEY (set_id) REFERENCES sets (id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    login TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER,
    user_id INTEGER, -- added to track the user
    known INTEGER, -- changed from BOOLEAN to INTEGER
    FOREIGN KEY (card_id) REFERENCES flashcards (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
)
""")

conn.commit()
conn.close()


print("Baza danych została zaktualizowana i wypełniona przykładowymi danymi.")
# Execute all add_* scripts in the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
for script in os.listdir(current_dir):
    if script.startswith("add_") and script.endswith(".py"):
        script_path = os.path.join(current_dir, script)
        print(f"Executing {script_path}...")
        subprocess.run(["python", script_path], check=True)
