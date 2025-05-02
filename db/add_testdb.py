import sqlite3

conn = sqlite3.connect("flashcards.db")
cursor = conn.cursor()

# Przykładowe zestawy i fiszki
sets = [
    ("Test DB",),  # Ensure each entry is a tuple
]

cursor.executemany("INSERT INTO sets (name) VALUES (?)", sets)

# Pobierz ID zestawu "Top 100 Phrasal Verbs"
cursor.execute("SELECT id FROM sets WHERE name = ?", sets[0])
set_id = cursor.fetchone()[0]

flashcards = [
("pies", "dog", set_id),
("kot", "cat", set_id),
("krowa", "cow", set_id),
("ptak", "bird", set_id),
]

cursor.executemany("INSERT INTO flashcards (word_pl, word_en, set_id) VALUES (?, ?, ?)", flashcards)

conn.commit()
conn.close()

print("Baza danych została zaktualizowana i wypełniona przykładowymi danymi.")