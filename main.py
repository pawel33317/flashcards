# backend/main.py
from fastapi import FastAPI, Request, Depends, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, Response
from pydantic import BaseModel
import sqlite3
from fastapi.responses import JSONResponse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests 
from fastapi import HTTPException
import os
import random
import string
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta

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

# Load CLIENT_ID and client_secret from files
with open("secret/google-id", "r") as f:
    CLIENT_ID = f.read().strip()

with open("secret/google-secret", "r") as f:
    CLIENT_SECRET = f.read().strip()

REDIRECT_URI = "http://localhost:8000/auth/callback"

with open("secret/token-secret", "r") as f:
    SECRET_KEY = f.read().strip()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 130

security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/auth/login")
def login():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=openid%20email%20profile"
    )
    return RedirectResponse(google_auth_url)

@app.get("/auth/callback")
def auth_callback(code: str):
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    # używamy 'requests' do POST
    token_response = requests.post(token_url, data=token_data)
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch token")

    token_json = token_response.json()

    # używamy 'google_requests' do weryfikacji tokena
    id_info = id_token.verify_oauth2_token(
        token_json["id_token"],
        google_requests.Request(),
        CLIENT_ID,
        clock_skew_in_seconds=10
    )

    # Extract user information
    user_email = id_info.get("email")
    user_name = id_info.get("name")

    # Add user to the database if not exists
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE login = ?", (user_email,)).fetchone()
    if not user:
        # Generate a random password
        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        conn.execute("INSERT INTO users (login, password) VALUES (?, ?)", (user_email, random_password))
        conn.commit()
        user = conn.execute("SELECT * FROM users WHERE login = ?", (user_email,)).fetchone()

    # Generate JWT with user ID
    access_token = create_access_token({"sub": user_email, "user_id": user["id"]})

    # Set token in an HTTP-only cookie and redirect to the homepage
    response = RedirectResponse(url="/")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=False,  # Set to True if using HTTPS
        samesite="lax"
    )
    return response

@app.post("/auth/logout")
def logout():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("access_token", path="/", samesite="lax")
    return response

@app.get("/auth/user")
def get_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=403, detail="Not authenticated")
    token_data = verify_token(access_token)
    user_email = token_data.get("sub")
    return {"email": user_email}

# Flashcards API

@app.get("/api/sets")
def get_sets(access_token: str = Cookie(None)):
    conn = get_db()
    sets = conn.execute("SELECT * FROM sets").fetchall()
    result = []
    # Read token from the cookie
    if not access_token:
        for set_row in sets:
            set_id = set_row["id"]
            result.append({
                **dict(set_row)
            })
    else:
        token_data = verify_token(access_token)
        user_email = token_data.get("sub")
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

@app.get("/api/flashcards")
def get_flashcards(set_id: int, access_token: str = Cookie(None)):
    conn = get_db()
    if not access_token:
        # raise HTTPException(status_code=403, detail="Not authenticated")
        cards = conn.execute("""
            SELECT flashcards.* 
            FROM flashcards 
            WHERE flashcards.set_id = ?
            ORDER BY RANDOM()
        """, (set_id,)).fetchall()
        return [dict(row) for row in cards]
    token_data = verify_token(access_token)
    user_email = token_data.get("sub")
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
    known: bool

@app.post("/api/stats")
def update_stats(stat: StatUpdate, access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=403, detail="Not authenticated")
    token_data = verify_token(access_token)
    user_id = token_data.get("user_id")
    conn = get_db()

    # Check if a stats entry exists for the given card_id and user_id
    existing_stat = conn.execute("""
        SELECT known 
        FROM stats 
        WHERE card_id = ? AND user_id = ?
    """, (stat.card_id, user_id)).fetchone()

    if existing_stat:
        # Update the existing stats entry
        if stat.known:
            conn.execute("""
                UPDATE stats 
                SET known = known + 1 
                WHERE card_id = ? AND user_id = ?
            """, (stat.card_id, user_id))
        else:
            conn.execute("""
                UPDATE stats 
                SET known = known - 2 
                WHERE card_id = ? AND user_id = ?
            """, (stat.card_id, user_id))
    else:
        # Insert a new stats entry
        initial_value = 1 if stat.known else -2
        conn.execute("""
            INSERT INTO stats (card_id, user_id, known) 
            VALUES (?, ?, ?)
        """, (stat.card_id, user_id, initial_value))

    conn.commit()
    return {"status": "ok"}