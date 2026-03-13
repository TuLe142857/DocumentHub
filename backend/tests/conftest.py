from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core import get_db_engine
from app.dependencies import get_db_session
from app.main import celery_worker, create_app
from app.models import *


@pytest.fixture(autouse=True)
def setup(monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", "ajshgdjhasdgjhasdjhadjhagdjahsgdajhdjhasgd")
    monkeypatch.setenv("SMTP_SERVER", "mailhog")
    monkeypatch.setenv("SMTP_PORT", "1025")
    monkeypatch.setenv("SMTP_USER", "testemail@testmail.com")
    monkeypatch.setenv("SMTP_PASSWORD", "password...")
    monkeypatch.setenv("SMTP_SEND_MAIL_FROM", "testemail@testmail.com")
    monkeypatch.setenv("SMTP_USE_TLS", "false")


@pytest.fixture(scope="module")
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    BaseModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    transaction.rollback()
    connection.close()
    session.close()


@pytest.fixture()
def client(db_engine, db_session):
    celery_worker.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )
    test_app = create_app()
    test_app.dependency_overrides[get_db_engine] = lambda: db_engine
    test_app.dependency_overrides[get_db_session] = lambda: db_session
    with TestClient(test_app) as client:
        yield client
