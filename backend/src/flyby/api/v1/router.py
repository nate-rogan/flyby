from fastapi import APIRouter

from .notes.router import router as notes_router
from .ollama.router import router as ollama_router
from .status.router import router as status_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(status_router)
v1_router.include_router(notes_router)
v1_router.include_router(ollama_router)
