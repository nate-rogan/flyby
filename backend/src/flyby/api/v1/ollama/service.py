import httpx

from .schemas import ModelOut


async def list_models(http: httpx.AsyncClient, base_url: str) -> list[ModelOut]:
    """Read-only: only ever calls Ollama's /api/tags, never generate/pull/delete."""
    resp = await http.get(f"{base_url}/api/tags", timeout=5.0)
    resp.raise_for_status()
    return [
        ModelOut(name=m["name"], size_gb=round(m.get("size", 0) / 1e9, 1))
        for m in resp.json().get("models", [])
    ]
