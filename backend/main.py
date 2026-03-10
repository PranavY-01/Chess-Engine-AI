"""
FastAPI Chess Engine Backend.
Entry point for the web server.

Run with: uvicorn main:app --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(
    title="Chess Engine API",
    description="Full chess engine with AI opponents and game tree analysis",
    version="1.0.0",
)

# CORS middleware — allow the React frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the exact frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(router)


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "message": "Chess Engine API is running",
        "version": "1.0.0",
        "endpoints": [
            "POST /game/start",
            "GET /game/state",
            "POST /game/move",
            "POST /ai/move",
            "GET /analysis/top-moves",
            "GET /game/legal-moves/{square}",
            "POST /game/undo",
            "POST /game/redo",
            "POST /game/set-difficulty",
        ]
    }
