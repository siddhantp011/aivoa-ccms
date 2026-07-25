from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.config import settings
from app.routes import complaints, chat
import app.models.complaint  # noqa: F401 - ensures model is registered before create_all

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AIVOA Customer Complaint Management System",
    description="AI-powered complaint intake for pharmaceutical API/FDF manufacturing QMS.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(complaints.router)
app.include_router(chat.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
