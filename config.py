with open("secret/google-id", "r") as f:
    CLIENT_ID = f.read().strip()

with open("secret/google-secret", "r") as f:
    CLIENT_SECRET = f.read().strip()

with open("secret/token-secret", "r") as f:
    SECRET_KEY = f.read().strip()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 130
REDIRECT_URI = "http://localhost:8000/auth/callback"