import os

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.dependencies import get_db_engine
from app.main import celery_worker, clear_settings_cache, create_app
from app.models import *


def setenv(k, v):
    os.environ[k] = v


@pytest.fixture(scope="session", autouse=True)
def setup():
    print("Setup for testing environment")

    clear_settings_cache()
    setenv("JWT_SECRET_KEY", "ajshgdjhasdgjhasdjhadjhagdjahsgdajhdjhasgd")

    setenv("SMTP_SERVER", "mailhog")
    setenv("SMTP_PORT", "1025")
    setenv("SMTP_USER", "testemail@testmail.com")
    setenv("SMTP_PASSWORD", "password...")
    setenv("SMTP_SEND_MAIL_FROM", "testemail@testmail.com")
    setenv("SMTP_USE_TLS", "false")

    # change db
    # this config copied fron docker/mysql/test_setup.sql
    setenv("MYSQL_DATABASE", "db_test")
    setenv("MYSQL_USER", "user_test")
    setenv("MYSQL_PASSWORD", "password_test")

    print("Setup for testing environment complete!")


@pytest.fixture(scope="session")
def app():
    engine = get_db_engine()
    ORMBase.metadata.drop_all(bind=engine)
    ORMBase.metadata.create_all(bind=engine)
    celery_worker.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )

    app = create_app()
    return app


@pytest.fixture(scope="function")
def db_session():
    db_engine = get_db_engine()
    with db_engine.connect() as connection:
        with Session(db_engine) as session:
            yield session
        print("[fixture] clear test data")
        # delete all data
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        for table in ORMBase.metadata.sorted_tables:
            connection.execute(table.delete())
        connection.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        connection.commit()
        print("[fixture] clear test data success")


@pytest.fixture(scope="function")
def client(app, db_session):
    with TestClient(app) as client:
        yield client
