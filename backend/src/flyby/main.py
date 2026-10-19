import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse
from psycopg_pool import AsyncConnectionPool

from flyby.api.v1.notes.service import ensure_schema
from flyby.api.v1.router import v1_router
from flyby.core.config import load_settings

log = logging.getLogger("flyby")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = app.state.settings = load_settings()
    app.state.http = httpx.AsyncClient()
    app.state.pool = None
    if settings.database_url:
        # prepare_threshold=None: Fly Managed Postgres sits behind PgBouncer,
        # which doesn't support server-side prepared statements.
        pool = AsyncConnectionPool(
            settings.database_url, open=False, kwargs={"prepare_threshold": None}
        )
        await pool.open()
        app.state.pool = pool
        try:
            await ensure_schema(pool)
        except Exception:
            log.exception("Postgres unavailable at startup — /api/v1/notes will error")
    yield
    await app.state.http.aclose()
    if app.state.pool:
        await app.state.pool.close()


app = FastAPI(title="flyby", lifespan=lifespan)
app.include_router(v1_router)


@app.get("/health", include_in_schema=False)
async def health() -> dict:
    # Deliberately DB-free: a Postgres blip shouldn't make Fly restart the machine.
    return {"ok": True}


@app.get("/{path:path}", include_in_schema=False)
async def spa(path: str) -> FileResponse:
    """Serve the built React app; unknown paths fall back to index.html."""
    static_dir = app.state.settings.static_dir.resolve()
    file = (static_dir / path).resolve()
    if path and file.is_file() and file.is_relative_to(static_dir):
        return FileResponse(file)
    return FileResponse(static_dir / "index.html")
