from datetime import datetime

from pydantic import BaseModel, Field


class NoteCreate(BaseModel):
    body: str = Field(min_length=1, max_length=280)


class NoteOut(BaseModel):
    id: int
    body: str
    created_at: datetime
