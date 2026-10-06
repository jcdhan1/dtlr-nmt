import pytest
from flask import Flask

from app import configure_cors


def create_cors_app(monkeypatch, environment, allowed_origins=None):
    monkeypatch.setenv("APP_ENV", environment)
    if allowed_origins is None:
        monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    else:
        monkeypatch.setenv("ALLOWED_ORIGINS", allowed_origins)

    app = Flask(__name__)
    configure_cors(app)
    app.add_url_rule("/", "index", lambda: "ok")
    return app


def test_development_allows_any_origin(monkeypatch):
    app = create_cors_app(monkeypatch, "development")

    response = app.test_client().get(
        "/", headers={"Origin": "http://localhost:3000"}
    )

    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"


def test_production_allows_configured_origin(monkeypatch):
    app = create_cors_app(
        monkeypatch,
        "production",
        "https://ui.example.com, https://staging.example.com",
    )

    response = app.test_client().get(
        "/", headers={"Origin": "https://ui.example.com"}
    )

    assert response.headers["Access-Control-Allow-Origin"] == "https://ui.example.com"


def test_production_does_not_allow_unlisted_origin(monkeypatch):
    app = create_cors_app(
        monkeypatch, "production", "https://ui.example.com"
    )

    response = app.test_client().get(
        "/", headers={"Origin": "https://other.example.com"}
    )

    assert "Access-Control-Allow-Origin" not in response.headers


def test_production_requires_allowed_origins(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)

    with pytest.raises(RuntimeError, match="ALLOWED_ORIGINS"):
        configure_cors(Flask(__name__))


def test_rejects_unknown_environment(monkeypatch):
    monkeypatch.setenv("APP_ENV", "prod")

    with pytest.raises(RuntimeError, match="APP_ENV"):
        configure_cors(Flask(__name__))
