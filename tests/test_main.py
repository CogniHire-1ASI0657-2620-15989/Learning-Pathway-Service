from fastapi.testclient import TestClient

from app.infrastructure.configuration.settings import get_settings
from app.main import app


def test_health_check(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://pathbridge:pathbridge@localhost:5432/learning_pathway_db")
    monkeypatch.setenv("IDENTITY_SERVICE_URL", "http://identity-service:8000")
    monkeypatch.setenv("GAP_ANALYSIS_SERVICE_URL", "http://gap-analysis-service:8000")
    monkeypatch.setenv("YOUTUBE_DATA_API_KEY", "test-api-key")
    monkeypatch.setenv("GATEWAY_USER_ID_HEADER", "X-User-Id")
    get_settings.cache_clear()

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"service": "learning-pathway", "status": "healthy"}


def test_registers_learning_path_routes() -> None:
    routes = {route.path for route in app.routes}

    assert "/api/v1/learning-paths" in routes
    assert "/api/v1/learning-paths/{job_id}" in routes
    assert "/api/v1/learning-paths/{learning_path_id}/items/{item_id}" in routes
    assert "/api/v1/learning-paths/{learning_path_id}/progress" in routes
    assert "/api/v1/certificates" in routes
    assert "/api/v1/certificates/{certificate_id}" in routes
    assert "/api/v1/certificates/{certificate_id}/synchronization" in routes
