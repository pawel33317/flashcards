import sqlite3

conn = sqlite3.connect("flashcards.db")
cursor = conn.cursor()

# Przykładowy zestaw i fiszki
set_name = "Test DB"

cursor.execute("INSERT INTO sets (name) VALUES (?)", (set_name,))

# Pobierz ID zestawu "Top 100 Business phrases"
cursor.execute("SELECT id FROM sets WHERE name = ?", (set_name,))
set_id = cursor.fetchone()[0]

flashcards = [
("pies", "dog"),
("kot", "cat"),
("krowa", "cow"),
("ptak", "bird"),
]

cursor.executemany("INSERT INTO flashcards (word_pl, word_en, set_id) VALUES (?, ?, ?)", [(word_pl, word_en, set_id) for word_pl, word_en in flashcards])

conn.commit()
conn.close()

print("Baza danych została zaktualizowana i wypełniona przykładowymi danymi.")