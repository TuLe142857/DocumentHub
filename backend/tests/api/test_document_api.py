import pytest

from app.models import *
from tests.utils.api_assertions import assert_response_error, assert_response_ok
from tests.utils.database import auth_client, seeded_db


def test_document_utilities_api(client):
    # document supported types
    supported_types = assert_response_ok(client.get("/documents/supported_types"))
    assert isinstance(supported_types, list)
    assert all(isinstance(t, str) for t in supported_types)

    # document max size in bytes
    max_size_bytes = assert_response_ok(client.get("/documents/max_size"))
    assert isinstance(max_size_bytes, int)

    # available document categories
    categories = assert_response_ok(client.get("/documents/categories"))
    assert isinstance(categories, list)
    assert all(
        (isinstance(cat.get("id"), int) and isinstance(cat.get("name"), str))
        for cat in categories
    )


def test_upload_document_api(auth_client, seeded_db):
    category = seeded_db.categories[0]

    response = auth_client.post(
        "/documents",
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


def test_get_document_list(auth_client):
    assert_response_ok(auth_client.get("/documents"))


def test_get_document_detail(auth_client, seeded_db):
    assert_response_ok(auth_client.get(f"/documents/{seeded_db.public_document.id}"))


@pytest.mark.parametrize(
    ["desc", "title", "category_id", "visibility", "tags"],
    [
        [None, None, None, None, None],
        ["Document desc updated", None, None, None, None],
        ["Document desc updated", "Document title updated", None, None, None],
        ["Document desc updated", "Document title updated", 1, None, None],
        [
            "Document desc updated",
            "Document title updated",
            1,
            DocumentVisibility.PUBLIC.value,
            None,
        ],
        [
            "Document desc updated",
            "Document title updated",
            1,
            DocumentVisibility.PRIVATE.value,
            None,
        ],
        [
            "Document desc updated",
            "Document title updated",
            1,
            DocumentVisibility.PRIVATE.value,
            [],
        ],
        [
            "Document desc updated",
            "Document title updated",
            1,
            DocumentVisibility.PRIVATE.value,
            ["updated_tag1", "updated_tag2", "updated_tag3"],
        ],
    ],
)
def test_update_document_api_success(
    auth_client, seeded_db, desc, title, category_id, visibility, tags
):
    document = seeded_db.public_document

    update_json = {}
    if desc:
        update_json["desc"] = desc
    if title:
        update_json["title"] = title
    if category_id:
        category = seeded_db.categories[0]
        for c in seeded_db.categories:
            if c.id != document.category_id:
                category = c
                break
        update_json["category_id"] = category.id
    if visibility:
        update_json["visibility"] = visibility
    if tags:
        update_json["tags"] = tags

    assert_response_ok(auth_client.patch(f"/documents/{document.id}", json=update_json))

    # check document after update
    document_after_update = assert_response_ok(
        auth_client.get(f"/documents/{document.id}")
    )
    if desc:
        assert document_after_update.get("desc") == desc
    if title:
        assert document_after_update.get("title") == title
    if category_id:
        assert document_after_update.get("category") == category.name
    if visibility:
        assert document_after_update.get("visibility") == visibility
    if tags:
        assert set(document_after_update.get("tags")) == set(tags)


@pytest.mark.parametrize("tag_name", ["tags1", "Tags1", "Tags_1"])
def test_document_tags_add_success(auth_client, seeded_db, tag_name):
    document = seeded_db.public_document

    # add tags
    assert_response_ok(auth_client.post(f"/documents/{document.id}/tags/{tag_name}"))

    # check document after updated
    updated_doc = assert_response_ok(auth_client.get(f"/documents/{document.id}"))
    assert tag_name in updated_doc.get("tags")


@pytest.mark.parametrize("tag_name", ["tags1", "Tags1", "Tags_1"])
def test_document_tags_remove_success(auth_client, seeded_db, tag_name):
    document = seeded_db.public_document

    # add tags
    assert_response_ok(auth_client.post(f"/documents/{document.id}/tags/{tag_name}"))

    # remove tags
    assert_response_ok(auth_client.delete(f"/documents/{document.id}/tags/{tag_name}"))

    # check after remove

    updated_document = assert_response_ok(auth_client.get(f"/documents/{document.id}"))
    assert not (tag_name in updated_document.get("tags"))


def test_document_like_success(auth_client, seeded_db):
    document = seeded_db.public_document

    assert_response_ok(auth_client.post(f"/documents/{document.id}/like"))

    # check
    document = assert_response_ok(auth_client.get(f"/documents/{document.id}"))
    assert document.get("liked") is True


def test_document_remove_like_success(auth_client, seeded_db):
    document = seeded_db.public_document

    assert_response_ok(auth_client.delete(f"/documents/{document.id}/like"))
    document = assert_response_ok(auth_client.get(f"/documents/{document.id}"))
    assert document.get("liked") is False


def test_soft_delete_document_success(auth_client, seeded_db):
    document = seeded_db.public_document

    # soft delete(move to trash)
    assert_response_ok(auth_client.delete(f"/documents/{document.id}"))

    # check trash list
    trash_list = assert_response_ok(
        auth_client.get(f"/documents?status={DocumentStatus.DELETED.value}")
    )
    assert any((d.get("id") == document.id for d in trash_list))


def test_restore_document_from_trash_success(auth_client, seeded_db):
    document = seeded_db.public_document

    # soft delete(move to trash)
    assert_response_ok(auth_client.delete(f"/documents/{document.id}"))

    assert_response_ok(auth_client.post(f"/documents/{document.id}/restore"))
    trash_list = assert_response_ok(
        auth_client.get(f"/documents?status={DocumentStatus.DELETED.value}")
    )
    assert all((d.get("id") != document.id for d in trash_list))


def test_download_document(auth_client, seeded_db):

    document = seeded_db.public_document
    available_formats = assert_response_ok(
        auth_client.get(f"/documents/{document.id}")
    ).get("available_formats")

    for doc_type in available_formats:
        url = assert_response_ok(
            auth_client.get(f"/documents/{document.id}/download?format={doc_type}")
        )
        assert isinstance(url, str)
