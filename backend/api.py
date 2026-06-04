# backend/api.py
# FastAPI application — exposes REST endpoints and serves the frontend.

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.pipeline import get_answer
from backend.modules.memory import chat_memory
from backend.modules.llm import get_active_backend

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── FastAPI app ────────────────────────────────────────────────────────────────
app = FastAPI(
    title       = "RAG Web Assistant API",
    description = "Retrieval-Augmented Generation chatbot powered by Groq + DuckDuckGo",
    version     = "2.0.0",
)

# Allow any origin in development (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_methods     = ["*"],
    allow_headers     = ["*"],
    allow_credentials = True,
)

# ── Request / Response schemas ────────────────────────────────────────────────
class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="User question")


class Source(BaseModel):
    title: str
    url:   str


class AskResponse(BaseModel):
    answer:     str
    key_points: list[str]
    sources:    list[Source]
    error:      str | None
    backend:    str


class HistoryEntry(BaseModel):
    role:    str
    content: str


# ── API Routes ─────────────────────────────────────────────────────────────────
@app.post("/api/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """
    Main RAG endpoint.

    Accepts a user question, runs the full pipeline (search → scrape → chunk
    → embed → retrieve → prompt → LLM), and returns a structured answer.
    """
    logger.info("[api] /ask  query=%r", request.query)

    result = get_answer(request.query)

    if result.get("error") and not result.get("answer"):
        raise HTTPException(status_code=400, detail=result["error"])

    return AskResponse(
        answer     = result["answer"],
        key_points = result.get("key_points", []),
        sources    = [Source(**s) for s in result.get("sources", [])],
        error      = result.get("error"),
        backend    = result.get("backend", ""),
    )


@app.post("/api/clear")
async def clear_memory():
    """Clear chat memory and start a fresh conversation."""
    chat_memory.clear()
    logger.info("[api] Memory cleared.")
    return {"status": "ok", "message": "Memory cleared."}


@app.get("/api/history", response_model=list[HistoryEntry])
async def get_history():
    """Return the current conversation history."""
    return [HistoryEntry(**entry) for entry in chat_memory.get_history()]


@app.get("/api/status")
async def status():
    """Health-check and backend info."""
    return {
        "status":  "ok",
        "backend": get_active_backend(),
        "memory":  len(chat_memory),
    }


# ── Serve static frontend ──────────────────────────────────────────────────────
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))

    # Catch-all: serve index.html for any unknown path (SPA routing)
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = FRONTEND_DIR / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIR / "index.html"))
else:
    logger.warning("[api] Frontend directory not found at %s", FRONTEND_DIR)

    @app.get("/")
    async def no_frontend():
        return {"message": "Frontend not found. API is running. POST /api/ask"}
