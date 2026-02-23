from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Any
import os
from dotenv import load_dotenv

from database import get_db, init_db, Interaction, HCP
from agent import run_agent

load_dotenv()

app = FastAPI(title="HCP CRM AI API", version="1.0.0")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


# ─── Pydantic Schemas ─────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    response: str
    form_data: Optional[dict] = None


class InteractionCreate(BaseModel):
    hcp_name: Optional[str] = None
    interaction_type: Optional[str] = "Meeting"
    date: Optional[str] = None
    time: Optional[str] = None
    attendees: Optional[str] = None
    topics_discussed: Optional[str] = None
    materials_shared: Optional[List[str]] = []
    samples_distributed: Optional[List[str]] = []
    sentiment: Optional[str] = "Neutral"
    outcomes: Optional[str] = None
    follow_up_actions: Optional[str] = None
    ai_suggested_followups: Optional[List[str]] = []


# ─── Chat Endpoint ─────────────────────────────────────────────────────────────

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint - routes user message through LangGraph agent."""
    try:
        history = [{"role": m.role, "content": m.content} for m in request.conversation_history]
        result = run_agent(history, request.message)
        return ChatResponse(response=result["response"], form_data=result.get("form_data"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


# ─── Interaction CRUD ──────────────────────────────────────────────────────────

@app.get("/api/interactions")
def get_interactions(db: Session = Depends(get_db)):
    interactions = db.query(Interaction).order_by(Interaction.created_at.desc()).all()
    return interactions


@app.get("/api/interactions/{interaction_id}")
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@app.post("/api/interactions")
def create_interaction(data: InteractionCreate, db: Session = Depends(get_db)):
    interaction = Interaction(**data.model_dump())
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


@app.put("/api/interactions/{interaction_id}")
def update_interaction(interaction_id: int, data: InteractionCreate, db: Session = Depends(get_db)):
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(interaction, key, value)
    db.commit()
    db.refresh(interaction)
    return interaction


@app.delete("/api/interactions/{interaction_id}")
def delete_interaction(interaction_id: int, db: Session = Depends(get_db)):
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    db.delete(interaction)
    db.commit()
    return {"message": "Deleted successfully"}


# ─── HCP Endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/hcps")
def get_hcps(db: Session = Depends(get_db)):
    return db.query(HCP).all()


@app.get("/api/hcps/search")
def search_hcps(q: str = "", db: Session = Depends(get_db)):
    hcps = db.query(HCP).filter(HCP.name.ilike(f"%{q}%")).all()
    return hcps


@app.get("/health")
def health():
    return {"status": "ok"}