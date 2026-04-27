import pytest
from app.models import *
from fastapi.testclient import TestClient
from app.core import get_settings
from tests.conftest import db_session
from .colection_factory import CollectionFactory
from .document_factory import DocumentFactory
from .user_factory import UserFactory
from .category_factory import CategoryFactory

TEST_PASSWORD = "password123"


@pytest.fixture
def role_user(db_session):
    return Role.get_or_create("USER", db_session)


@pytest.fixture
def role_admin(db_session):
    return Role.get_or_create("ADMIN", db_session)


@pytest.fixture
def user(db_session, role_user):
    print("Create User for test...")
    user = User(
        email="testuser@mail.com",
        username="test_user",
        role=role_user,
        profile=UserProfile(),
    )
    user.set_password(TEST_PASSWORD)
    db_session.add(user)
    db_session.commit()
    print("Create User for test success!")
    return user


@pytest.fixture
def admin(db_session, role_admin):
    print("Create Admin for test...")
    admin = User(
        email="testadmin@mail.com",
        username="test_admin",
        role=role_admin,
        profile=UserProfile(),
    )
    admin.set_password(TEST_PASSWORD)
    db_session.add(admin)
    db_session.commit()
    print("Create Admin for test success!")
    return admin


@pytest.fixture(scope="function")
def auth_client(app, user):
    settings = get_settings()
    with TestClient(app) as client:
        client.base_url = f"{client.base_url}".rstrip("/") + settings.API_V1_STR
        login_data = {
            "identity": user.username,
            "password": TEST_PASSWORD,
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200

        # auth cookie will auto write to this TestClient object when login success
        yield client


@pytest.fixture(scope="function")
def admin_client(app, admin):
    settings = get_settings()
    with TestClient(app) as client:
        client.base_url = f"{client.base_url}".rstrip("/") + settings.API_V1_STR
        login_data = {
            "identity": admin.username,
            "password": TEST_PASSWORD,
        }

        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        yield client


@pytest.fixture
def categories(db_session) -> list[Category]:
    print("Create Categories for test...")
    categories = []
    for c in ["Python", "FastAPI", "Pydantic", "SQLAlchemy", "ComputerScience"]:
        category = Category(name=c)
        db_session.add(category)
        categories.append(category)
    db_session.commit()
    print("Create Categories for test success!")
    return categories


@pytest.fixture
def report_reason(db_session) -> list[ReportReason]:
    print("Create Report Reason for test...")
    report_reasons = []
    for r in [
        "SPAM",
        "SCAM",
        "COPYRIGHT_VIOLATION",
        "FAKE_CONTENT",
    ]:
        reason = ReportReason(code=r)
        db_session.add(reason)
        report_reasons.append(reason)
    db_session.commit()
    print("Create Report Reasons for test success!")
    return report_reasons


@pytest.fixture
def collection_factory(db_session) -> CollectionFactory:
    return CollectionFactory(db_session)


@pytest.fixture
def document_factory(db_session) -> DocumentFactory:
    return DocumentFactory(db_session)


@pytest.fixture
def user_factory(db_session) -> UserFactory:
    return UserFactory(db_session)

@pytest.fixture
def category_factory(db_session) -> CategoryFactory:
    return CategoryFactory(db_session)
