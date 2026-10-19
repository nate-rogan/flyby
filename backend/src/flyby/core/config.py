import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Everything optional is off when its env var is unset — the site still runs."""

    database_url: str | None
    ollama_base_url: str | None
    static_dir: Path
    fly_app: str
    fly_region: str
    fly_machine: str
    ts_status: str
    ts_ip: str


def load_settings() -> Settings:
    env = os.environ.get
    return Settings(
        database_url=env("DATABASE_URL") or None,
        ollama_base_url=(env("OLLAMA_BASE_URL") or "").rstrip("/") or None,
        static_dir=Path(env("STATIC_DIR", "/app/frontend/dist")),
        fly_app=env("FLY_APP_NAME", "local"),
        fly_region=env("FLY_REGION", "local"),
        fly_machine=env("FLY_MACHINE_ID", "local"),
        # Exported by start.sh after it tries to bring Tailscale up
        ts_status=env("TS_STATUS", "disabled"),
        ts_ip=env("TS_IP", ""),
    )
