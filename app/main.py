from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from app.models.schemas import ChatRequest, ChatResponse
from app.services.agent import SHLAgentService
from app.services.catalog_store import load_vector_store

app = FastAPI(title="SHL Assessment Assistant", version="1.0.0")

vector_store = load_vector_store("data/chroma_db")
agent = SHLAgentService(vector_store=vector_store)


@app.get("/")
def root() -> dict:
    """Home has no chat UI; use `/docs` or POST `/chat`."""
    return {
        "service": "SHL Assessment Assistant",
        "docs": "/docs",
        "health": "/health",
        "chat": {"method": "POST", "path": "/chat"},
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    try:
        return agent.handle_chat(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {exc}") from exc
