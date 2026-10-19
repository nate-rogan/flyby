from typing import Annotated

import httpx
from fastapi import Depends, HTTPException, Request
from psycopg_pool import AsyncConnectionPool

from flyby.core.config import Settings


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_pool(request: Request) -> AsyncConnectionPool:
    pool = request.app.state.pool
    if pool is None:
        raise HTTPException(503, "Database not configured (set DATABASE_URL)")
    return pool


def get_http(request: Request) -> httpx.AsyncClient:
    return request.app.state.http


SettingsDep = Annotated[Settings, Depends(get_settings)]
Pool = Annotated[AsyncConnectionPool, Depends(get_pool)]
Http = Annotated[httpx.AsyncClient, Depends(get_http)]
