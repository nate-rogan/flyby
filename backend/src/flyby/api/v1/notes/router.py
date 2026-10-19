from fastapi import APIRouter

from flyby.core.deps import Pool

from . import service
from .schemas import NoteCreate, NoteOut

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=list[NoteOut])
async def list_notes(pool: Pool) -> list[NoteOut]:
    return await service.list_notes(pool)


@router.post("", response_model=NoteOut, status_code=201)
async def add_note(body: NoteCreate, pool: Pool) -> NoteOut:
    return await service.add_note(pool, body.body)
