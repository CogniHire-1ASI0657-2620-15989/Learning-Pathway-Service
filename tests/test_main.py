from fastapi.testclient import TestClient

from app.infrastructure.configuration.settings import get_settings
from app.main import app


def test_health_check(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://pathbridge:pathbridge@localhost:5432/learning_pathway_db")
    get_settings.cache_clear()

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"service": "learning-pathway", "status": "healthy"}
