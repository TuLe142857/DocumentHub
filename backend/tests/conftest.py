from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine

from app.core import get_db_engine, get_settings
from app.main import create_app


@pytest.fixture(autouse=True)
def setup(monkeypatch):
    monkeypatch.setenv("SMTP_SERVER", "mailhog")
    monkeypatch.setenv("SMTP_PORT", "1025")
    monkeypatch.setenv("SMTP_USER", "testemail@testmail.com")
    monkeypatch.setenv("SMTP_PASSWORD", "password...")
    monkeypatch.setenv("SMTP_SEND_MAIL_FROM", "testemail@testmail.com")
    monkeypatch.setenv("SMTP_USE_TLS", "false")


@pytest.fixture()
def client():
    test_app = create_app()
    engine = create_engine("sqlite:///:memory:")
    test_app.dependency_overrides[get_db_engine] = lambda: engine
    with TestClient(test_app) as client:
        yield client
