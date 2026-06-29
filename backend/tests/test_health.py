from backend.app.api.v1.endpoints.health import read_health
from backend.app.main import create_app


def test_app_uses_expected_api_prefix() -> None:
    app = create_app()

    assert app.openapi_url == "/api/v1/openapi.json"
    assert app.docs_url == "/api/v1/docs"


def test_health_handler_returns_ok() -> None:
    response = read_health()

    assert response.model_dump() == {"status": "ok", "service": "backend"}
