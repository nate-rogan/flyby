import httpx
import pytest
from fastapi.testclient import TestClient

from flyby.core.deps import get_http
from flyby.main import app

FAKE_OLLAMA = "http://ollama.test:11434"


@pytest.fixture
def make_client(tmp_path, monkeypatch):
    (tmp_path / "index.html").write_text("<h1>spa</h1>")
    (tmp_path / "app.js").write_text("console.log(1)")
    monkeypatch.setenv("STATIC_DIR", str(tmp_path))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)

    def make(**env):
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        return TestClient(app)

    yield make
    app.dependency_overrides.clear()


def mock_ollama(handler) -> None:
    app.dependency_overrides[get_http] = lambda: httpx.AsyncClient(
        transport=httpx.MockTransport(handler)
    )


def test_health(make_client):
    with make_client() as client:
        assert client.get("/health").json() == {"ok": True}


def test_status_reports_disabled_integrations(make_client):
    with make_client() as client:
        body = client.get("/api/v1/status").json()
    assert body["tailscale"]["status"] == "disabled"
    assert body["database"] is False
    assert body["ollama"] is False


def test_notes_503_without_database(make_client):
    with make_client() as client:
        assert client.get("/api/v1/notes").status_code == 503


def test_ollama_503_when_unconfigured(make_client):
    with make_client() as client:
        assert client.get("/api/v1/ollama/models").status_code == 503


def test_ollama_lists_models_via_tags_only(make_client):
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.path)
        return httpx.Response(200, json={"models": [{"name": "llama3:8b", "size": 4_700_000_000}]})

    mock_ollama(handler)
    with make_client(OLLAMA_BASE_URL=FAKE_OLLAMA) as client:
        resp = client.get("/api/v1/ollama/models")

    assert resp.json() == [{"name": "llama3:8b", "size_gb": 4.7}]
    assert seen == ["/api/tags"]


def test_ollama_502_when_unreachable(make_client):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("no route")

    mock_ollama(handler)
    with make_client(OLLAMA_BASE_URL=FAKE_OLLAMA) as client:
        assert client.get("/api/v1/ollama/models").status_code == 502


def test_spa_serves_files_and_falls_back(make_client):
    with make_client() as client:
        assert client.get("/app.js").text == "console.log(1)"
        assert "spa" in client.get("/some/deep/route").text
        assert "spa" in client.get("/..%2F..%2Fetc%2Fpasswd").text
