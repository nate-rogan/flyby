from fastapi import APIRouter
from pydantic import BaseModel

from flyby.core.deps import SettingsDep

router = APIRouter(prefix="/status", tags=["status"])


class Tailscale(BaseModel):
    status: str
    ip: str


class StatusOut(BaseModel):
    app: str
    region: str
    machine: str
    tailscale: Tailscale
    database: bool
    ollama: bool


@router.get("", response_model=StatusOut)
async def get_status(settings: SettingsDep) -> StatusOut:
    return StatusOut(
        app=settings.fly_app,
        region=settings.fly_region,
        machine=settings.fly_machine,
        tailscale=Tailscale(status=settings.ts_status, ip=settings.ts_ip),
        database=settings.database_url is not None,
        ollama=settings.ollama_base_url is not None,
    )
