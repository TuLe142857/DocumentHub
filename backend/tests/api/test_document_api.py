import pytest
from sqlalchemy import select

from app.models import *
from tests.utils.api_assertions import assert_response_error, assert_response_ok
from tests.utils.db_fixture import category, document, role_user, user


def test_get_document_supported_type(client):
    assert_response_ok(client.get("/api/documents/supported_types"))


def test_upload_document_api(client, user, category):
    # login
    assert_response_ok(
        client.post(
            "/api/auth/login",
            json={"identity": user.username, "password": "password12345"},
        )
    )

    response = client.post(
        "/api/documents",
        data={
            "title": "test document",
            "visibility": "PRIVATE",
            "category_id": str(category.id),
            "tags": ["t1", "t2"],
            "desc": "description",
        },
        files={"file": ("document.pdf", b"fake binary content")},
    )

    assert_response_ok(response)


def test_get_document_list(client, user, category):
    # login
    assert_response_ok(
        client.post(
            "/api/auth/login",
            json={"identity": user.username, "password": "password12345"},
        )
    )

    assert_response_ok(client.get("/api/documents"))


def test_get_document_detail(client, user, category, document):
    # login
    assert_response_ok(
        client.post(
            "/api/auth/login",
            json={"identity": user.username, "password": "password12345"},
        )
    )

    assert_response_ok(client.get(f"/api/documents/{document.id}"))


@pytest.mark.parametrize(
    ["desc", "title", "category_id", "visibility"],
    [
        [None, None, None, None],
        ["Document desc updated", None, None, None],
        ["Document desc updated", "Document title updated", None, None],
        ["Document desc updated", "Document title updated", 1, None],
        [
            "Document desc updated",
            "Document title updated",
            1,
            DocumentVisibility.PUBLIC.value,
        ],
        [
            "Document desc updated",
            "Document title updated",
            1,
            DocumentVisibility.PRIVATE.value,
        ],
    ],
)
def test_update_document_api_success(
    db_session, client, user, document, desc, title, category_id, visibility
):
    # login
    assert_response_ok(
        client.post(
            "/api/auth/login",
            json={"identity": user.username, "password": "password12345"},
        )
    )

    update_json = {}
    if desc:
        update_json["desc"] = desc
    if title:
        update_json["title"] = title
    if category_id:
        category: Category = db_session.execute(
            select(Category).where(Category.id == category_id)
        ).scalar_one_or_none()
        if not category:
            category = Category(name="jsdgfshjsd", id=category_id)
            db_session.add(category)
            db_session.commit()
        update_json["category_id"] = category_id
    if visibility:
        update_json["visibility"] = visibility

    assert_response_ok(client.patch(f"/api/documents/{document.id}", json=update_json))

    # check document after update

    document_after_update = assert_response_ok(
        client.get(f"/api/documents/{document.id}")
    )
    if desc:
        assert document_after_update.get("desc") == desc
    if title:
        assert document_after_update.get("title") == title
    if category_id:
        assert document_after_update.get("category") == category.name
    if visibility:
        assert document_after_update.get("visibility") == visibility


@pytest.mark.parametrize(
    ["desc", "title", "category_id", "visibility", "expected_error"],
    [
        [None, None, None, None, None],
    ],
)
def test_document_update_failed(
    client, user, document, desc, title, category_id, visibility, expected_error
):
    assert True


def test_document_tags_add_success():
    pass


def test_document_tags_add_failed():
    pass


def test_document_tags_remove_success():
    pass


def test_document_tags_remove_failed():
    pass


def test_document_like_success():
    pass


def test_document_like_failed_no_auth():
    pass
