import pytest

from app.models import *


@pytest.fixture
def role_user(db_session):
    role = Role.get_or_create("USER", db_session)
    db_session.add(role)
    db_session.commit()
    return role


@pytest.fixture
def role_admin(db_session):
    role = Role.get_or_create("ADMIN", db_session)
    db_session.add(role)
    db_session.commit()
    return role


@pytest.fixture
def user(db_session, role_user):
    user = User(
        username="test_user",
        email="test_user@mail.com",
        role=role_user,
        profile=UserProfile(),
    )
    user.set_password("password12345")
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def admin(db_session, role_admin):
    admin = User(
        username="test_admin",
        email="test_admin@mail.com",
        role=role_admin,
        profile=UserProfile(),
    )
    admin.set_password("password12345")
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def category(db_session):
    category = Category(name="Test Category")
    db_session.add(category)
    db_session.commit()
    return category


@pytest.fixture
def document(db_session, category, user):
    document = Document(
        title="Test Document Title",
        desc="Test Document Description",
        category=category,
        owner=user,
        visibility=DocumentVisibility.PUBLIC,
        file_type=".doc",
        file_preview_object_key="file_preview_object_key",
        file_object_key="file_object_key",
        sha256sum="sha256sum",
        md5sum="md5sum",
        status=DocumentStatus.READY,
        thumbnail_object_key="thumbnail_object_key",
    )
    db_session.add(document)
    db_session.commit()
    return document
