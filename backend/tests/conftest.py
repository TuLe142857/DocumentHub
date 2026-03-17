import os

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.dependencies import get_db_engine, get_db_session
from app.main import celery_worker, create_app
from app.models import *


def setenv(k, v):
    os.environ[k] = v


@pytest.fixture(scope="session", autouse=True)
def setup():
    setenv("JWT_SECRET_KEY", "ajshgdjhasdgjhasdjhadjhagdjahsgdajhdjhasgd")
    setenv("SMTP_SERVER", "mailhog")
    setenv("SMTP_PORT", "1025")
    setenv("SMTP_USER", "testemail@testmail.com")
    setenv("SMTP_PASSWORD", "password...")
    setenv("SMTP_SEND_MAIL_FROM", "testemail@testmail.com")
    setenv("SMTP_USE_TLS", "false")


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    ORMBase.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="session")
def app(db_engine):
    celery_worker.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )

    app = create_app()
    app.dependency_overrides[get_db_engine] = lambda: db_engine
    return app


@pytest.fixture
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(app, db_session):
    app.dependency_overrides[get_db_session] = lambda: db_session
    with TestClient(app) as client:
        yield client
