# backend/main.py
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
from fastapi.responses import JSONResponse

app = FastAPI()
# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("index.html")


DATABASE = "db/flashcards.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Auth

class TokenData(BaseModel):
    token: str

# Flashcards API

@app.get("/api/sets")
def get_sets():
    conn = get_db()
    sets = conn.execute("SELECT * FROM sets").fetchall()
    result = []
    for set_row in sets:
        set_id = set_row["id"]
        total = conn.execute("SELECT COUNT(*) FROM flashcards WHERE set_id = ?", (set_id,)).fetchone()[0]
        known = conn.execute("SELECT COUNT(*) FROM flashcards WHERE set_id = ? AND value > 0", (set_id,)).fetchone()[0]
        unknown = conn.execute("SELECT COUNT(*) FROM flashcards WHERE set_id = ? AND value < 0", (set_id,)).fetchone()[0]
        new_cards = conn.execute("SELECT COUNT(*) FROM flashcards WHERE set_id = ? AND value = 0", (set_id,)).fetchone()[0]
        result.append({
            **dict(set_row),
            "total": total,
            "known": known,
            "unknown": unknown,
            "new": new_cards
        })
    return result

@app.get("/api/flashcards")
def get_flashcards(set_id: int):
    conn = get_db()
    cards = conn.execute(
        "SELECT * FROM flashcards WHERE set_id = ? AND value <= 0 ORDER BY RANDOM()", (set_id,)
    ).fetchall()
    return [dict(row) for row in cards]

class StatUpdate(BaseModel):
    card_id: int
    known: bool

@app.post("/api/stats")
def update_stats(stat: StatUpdate):
    conn = get_db()
    if stat.known:
        conn.execute("UPDATE flashcards SET value = value + 1 WHERE id = ?", (stat.card_id,))
    else:
        conn.execute("UPDATE flashcards SET value = value - 2 WHERE id = ?", (stat.card_id,))
    conn.execute("INSERT INTO stats (card_id, known) VALUES (?, ?)", (stat.card_id, int(stat.known)))
    conn.commit()
    return {"status": "ok"}