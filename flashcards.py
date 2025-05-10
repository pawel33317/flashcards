from fastapi import APIRouter, HTTPException, Cookie
from database import get_db
from auth import verify_token
from pydantic import BaseModel

flashcards_router = APIRouter()

@flashcards_router.get("/sets")
def get_sets(access_token: str = Cookie(None)):
    conn = get_db()
    sets = conn.execute("SELECT * FROM sets").fetchall()
    result = []
    if not access_token:
        for set_row in sets:
            result.append({**dict(set_row)})
    else:
        token_data = verify_token(access_token)
        user_id = token_data.get("user_id")
        for set_row in sets:
            set_id = set_row["id"]
            total = conn.execute("SELECT COUNT(*) FROM flashcards WHERE set_id = ?", (set_id,)).fetchone()[0]
            known = conn.execute("""
                SELECT COUNT(*) 
                FROM stats 
                JOIN flashcards ON stats.card_id = flashcards.id AND stats.user_id = ?
                WHERE flashcards.set_id = ? AND stats.known > 0
            """, (user_id, set_id)).fetchone()[0]
            unknown = conn.execute("""
                SELECT COUNT(*) 
                FROM stats 
                LEFT JOIN flashcards ON stats.card_id = flashcards.id AND stats.user_id = ?
                WHERE flashcards.set_id = ? AND stats.known < 0
            """, (user_id, set_id)).fetchone()[0]
            new_cards = total - known - unknown
            result.append({
                **dict(set_row),
                "total": total,
                "known": known,
                "unknown": unknown,
                "new": new_cards
            })
    return result

@flashcards_router.get("/flashcards")
def get_flashcards(set_id: int, access_token: str = Cookie(None)):
    conn = get_db()
    if not access_token:
        cards = conn.execute("""
            SELECT flashcards.* 
            FROM flashcards 
            WHERE flashcards.set_id = ?
            ORDER BY RANDOM()
        """, (set_id,)).fetchall()
        return [dict(row) for row in cards]
    token_data = verify_token(access_token)
    user_id = token_data.get("user_id")
    cards = conn.execute("""
        SELECT flashcards.* 
        FROM flashcards 
        LEFT JOIN stats ON flashcards.id = stats.card_id AND stats.user_id = ?
        WHERE flashcards.set_id = ? AND (stats.known IS NULL OR stats.known <= 0)
        ORDER BY RANDOM()
    """, (user_id, set_id,)).fetchall()
    return [dict(row) for row in cards]

class StatUpdate(BaseModel):
    card_id: int
    known: int

@flashcards_router.post("/stats")
def update_stats(stat: StatUpdate, access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=403, detail="Not authenticated")
    token_data = verify_token(access_token)
    user_id = token_data.get("user_id")
    conn = get_db()

    point_value = 0
    if stat.known == 1:
        point_value = 1
        print("point_value = 1")
    elif stat.known == -1:
        print("point_value = -1")
        point_value = -1
    elif stat.known == -2:
        print("point_value = -2")
        point_value = -2

    existing_stat = conn.execute("""
        SELECT known 
        FROM stats 
        WHERE card_id = ? AND user_id = ?
    """, (stat.card_id, user_id)).fetchone()

    if existing_stat:
        conn.execute("""
            UPDATE stats 
            SET known = known + ?
            WHERE card_id = ? AND user_id = ?
            """, (point_value, stat.card_id, user_id))
    else:
        conn.execute("""
            INSERT INTO stats (card_id, user_id, known) 
            VALUES (?, ?, ?)
        """, (stat.card_id, user_id, point_value))

    conn.commit()
    return {"status": "ok"}


@flashcards_router.get("/resetSet")
def update_stats(set_id: int, access_token: str = Cookie(None)):
    print("resetSet")
    if not access_token:
        raise HTTPException(status_code=403, detail="Not authenticated")

    token_data = verify_token(access_token)
    user_id = token_data.get("user_id")
    conn = get_db()

    conn.execute("""
        DELETE FROM stats 
        WHERE user_id = ? AND card_id IN (
            SELECT id FROM flashcards WHERE set_id = ?
        )
    """, (user_id, set_id))

    conn.commit()
    return {"status": "ok"}