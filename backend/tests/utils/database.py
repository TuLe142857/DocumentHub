from dataclasses import dataclass

import pytest
from sqlalchemy.orm import Session

from app.models import *


@dataclass
class SeededData:
    db_session: Session

    default_password: str
    role_admin: Role
    admin: User

    role_user: Role
    user: User

    public_document: Document
    private_document: Document

    collection: Collection

    categories: list[Category]
    tags: list[Tag]

    report_reasons: list[ReportReason]


@pytest.fixture(scope="function")
def seeded_db(db_session) -> SeededData:
    print("Seed DB for test...")

    # default password for user & admin
    default_password = "password12345"

    # create role
    role_user = Role.get_or_create("USER", db_session)
    role_admin = Role.get_or_create("ADMIN", db_session)
    db_session.add(role_user)
    db_session.add(role_admin)

    # create user & admin
    user = User(
        username="test_user",
        email="test_user@mail.com",
        role=role_user,
        profile=UserProfile(),
    )
    user.set_password(default_password)
    db_session.add(user)

    admin = User(
        username="test_admin",
        email="test_admin@mail.com",
        role=role_admin,
        profile=UserProfile(),
    )
    admin.set_password(default_password)
    db_session.add(admin)

    # categories
    categories = []
    for c in ["Python", "FastAPI", "Pydantic", "SQLAlchemy", "ComputerScience"]:
        category = Category(name=c)
        db_session.add(category)
        categories.append(category)

    # tags
    tags = []
    for t in ["tag1", "tag2", "tag3", "tag4"]:
        tag = Tag(name=t)
        db_session.add(tag)
        tags.append(tag)

    # document
    public_document = Document(
        title="Test Document Title",
        desc="Test Document Description",
        category=categories[0],
        owner=user,
        visibility=DocumentVisibility.PUBLIC,
        file_type=".doc",
        file_preview_object_key="file_preview_object_key_pub",
        file_object_key="file_object_key_pub",
        sha256sum="sha256sum",
        md5sum="md5sum",
        status=DocumentStatus.READY,
        thumbnail_object_key="thumbnail_object_key",
    )
    db_session.add(public_document)

    private_document = Document(
        title="Private Document Title",
        desc="Private Document Description",
        category=categories[1],
        owner=user,
        visibility=DocumentVisibility.PRIVATE,
        file_type=".doc",
        file_preview_object_key="file_preview_object_key_pri",
        file_object_key="file_object_key_pri",
        sha256sum="sha256sum",
        md5sum="md5sum",
        status=DocumentStatus.READY,
        thumbnail_object_key="thumbnail_object_key",
    )
    db_session.add(private_document)

    # collection
    collection = Collection(owner=user, name="Test Collection")
    collection_item1 = CollectionItem(collection=collection, document=public_document)
    collection_item2 = CollectionItem(collection=collection, document=private_document)
    db_session.add(collection)
    db_session.add(collection_item1)
    db_session.add(collection_item2)

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

    try:
        db_session.commit()
        print("Seed DB for test success")
    except Exception as e:
        pytest.fail(f"Seed DB for test failed\nException: {str(e)}")

    return SeededData(
        db_session=db_session,
        role_admin=role_admin,
        role_user=role_user,
        admin=admin,
        user=user,
        default_password=default_password,
        tags=tags,
        categories=categories,
        public_document=public_document,
        private_document=private_document,
        collection=collection,
        report_reasons=report_reasons,
    )


@pytest.fixture(scope="function")
def auth_client(client, seeded_db):
    login_data = {
        "identity": seeded_db.user.username,
        "password": seeded_db.default_password,
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200

    # auth cookie will auto write to this TestClient object when login success
    return client


@pytest.fixture(scope="function")
def admin_client(client, seeded_db):
    login_data = {
        "identity": seeded_db.admin.username,
        "password": seeded_db.default_password,
    }

    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    return client
