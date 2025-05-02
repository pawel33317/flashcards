from fastapi import APIRouter, HTTPException, Cookie
from fastapi.responses import JSONResponse, RedirectResponse
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from jose import jwt, JWTError
from datetime import datetime, timedelta
import requests
import random
import string
from database import get_db
import config

auth_router = APIRouter()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@auth_router.get("/login")
def login():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={config.CLIENT_ID}"
        f"&redirect_uri={config.REDIRECT_URI}"
        "&scope=openid%20email%20profile"
    )
    return RedirectResponse(google_auth_url)

@auth_router.get("/callback")
def auth_callback(code: str):
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "code": code,
        "client_id": config.CLIENT_ID,
        "client_secret": config.CLIENT_SECRET,
        "redirect_uri": config.REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    token_response = requests.post(token_url, data=token_data)
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to fetch token")

    token_json = token_response.json()
    id_info = id_token.verify_oauth2_token(
        token_json["id_token"],
        google_requests.Request(),
        config.CLIENT_ID,
        clock_skew_in_seconds=10
    )

    user_email = id_info.get("email")
    user_name = id_info.get("name")
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE login = ?", (user_email,)).fetchone()
    if not user:
        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        conn.execute("INSERT INTO users (login, name, password) VALUES (?, ?, ?)", (user_email, user_name, random_password))
        conn.commit()
        user = conn.execute("SELECT * FROM users WHERE login = ?", (user_email,)).fetchone()

    access_token = create_access_token({"sub": user_email, "user_id": user["id"]})
    response = RedirectResponse(url="/")
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=False,
        samesite="lax"
    )
    return response

@auth_router.post("/logout")
def logout():
    response = JSONResponse(content={"message": "Logged out"})
    response.delete_cookie("access_token", path="/", samesite="lax")
    return response

@auth_router.get("/user")
def get_user(access_token: str = Cookie(None)):
    if not access_token:
        raise HTTPException(status_code=403, detail="Not authenticated")
    token_data = verify_token(access_token)
    user_email = token_data.get("sub")
    return {"email": user_email}
