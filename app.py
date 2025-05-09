from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from auth import auth_router
from flashcards import flashcards_router

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve favicon
@app.get("/favicon.ico")
def favicon():
    return FileResponse("static/logo.ico")

# Include routers
app.include_router(auth_router, prefix="/auth")
app.include_router(flashcards_router, prefix="/api")

@app.get("/")
def serve_index():
    return FileResponse("index.html")