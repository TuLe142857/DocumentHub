from app.models import *
from app.schemas import collection_schema
from tests.utils.api_assertions import assert_response_error, assert_response_ok
from tests.utils.db_fixture import (
    auth_client,
    category,
    collection,
    document,
    role_admin,
    role_user,
    user,
)


def test_create_collection_success(auth_client):
    assert_response_ok(
        auth_client.post("/collections", json={"name": "test collection"})
    )


def test_update_collection_success(auth_client, collection):
    assert_response_ok(
        auth_client.patch(
            f"/collections/{collection.id}", json={"new_name": "new name"}
        )
    )


def test_delete_collection_success(auth_client, collection):
    assert_response_ok(auth_client.delete(f"/collections/{collection.id}"))


def test_list_collections_success(auth_client, collection):
    assert_response_ok(auth_client.get("/collections"))


def test_list_document_in_collection_success(auth_client, collection):
    assert_response_ok(auth_client.get(f"/collections/{collection.id}/items"))


def test_add_document_to_collection_success(
    auth_client, collection, user, db_session, category
):
    new_document = document = Document(
        title="Test Document Title kjahdkjahsdk",
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
    db_session.add(new_document)
    db_session.commit()

    assert_response_ok(
        auth_client.put(f"/collections/{collection.id}/items/{new_document.id}")
    )


def test_delete_document_from_collection_success(auth_client, collection, document):
    assert_response_ok(
        auth_client.delete(f"/collections/{collection.id}/items/{document.id}")
    )
