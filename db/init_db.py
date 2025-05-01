import sqlite3

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
    value INTEGER DEFAULT 0, -- added to track flashcard score
    FOREIGN KEY (set_id) REFERENCES sets (id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    card_id INTEGER,
    known INTEGER, -- changed from BOOLEAN to INTEGER
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (card_id) REFERENCES flashcards (id)
)
""")

conn.commit()
conn.close()

print("Baza danych została zaktualizowana i wypełniona przykładowymi danymi.")