from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from app.routers import auth, events, sharing, history
from app.database import engine, Base
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Event Scheduler API",
    description="A collaborative event scheduling API with version history",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])
app.include_router(sharing.router, prefix="/api/events", tags=["Sharing"])
app.include_router(history.router, prefix="/api/events", tags=["History"])

@app.get("/")
def read_root():
    return {"message": "Event Scheduler API"}