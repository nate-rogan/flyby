import httpx
from fastapi import APIRouter, HTTPException

from flyby.core.deps import Http, SettingsDep

from . import service
from .schemas import ModelOut

router = APIRouter(prefix="/ollama", tags=["ollama"])


@router.get("/models", response_model=list[ModelOut])
async def list_models(settings: SettingsDep, http: Http) -> list[ModelOut]:
    if settings.ollama_base_url is None:
        raise HTTPException(503, "Ollama not configured (set OLLAMA_BASE_URL)")
    try:
        return await service.list_models(http, settings.ollama_base_url)
    except httpx.HTTPError as exc:
        raise HTTPException(502, f"Ollama unreachable over Tailscale: {type(exc).__name__}")
