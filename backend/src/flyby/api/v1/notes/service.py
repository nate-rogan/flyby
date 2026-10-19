from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from .schemas import NoteOut

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id         SERIAL PRIMARY KEY,
    body       TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
)
"""


async def ensure_schema(pool: AsyncConnectionPool) -> None:
    async with pool.connection() as conn:
        await conn.execute(SCHEMA)


async def list_notes(pool: AsyncConnectionPool, limit: int = 20) -> list[NoteOut]:
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            "SELECT id, body, created_at FROM notes ORDER BY id DESC LIMIT %s", (limit,)
        )
        return [NoteOut(**row) for row in await cur.fetchall()]


async def add_note(pool: AsyncConnectionPool, body: str) -> NoteOut:
    async with pool.connection() as conn, conn.cursor(row_factory=dict_row) as cur:
        await cur.execute(
            "INSERT INTO notes (body) VALUES (%s) RETURNING id, body, created_at", (body,)
        )
        return NoteOut(**await cur.fetchone())
