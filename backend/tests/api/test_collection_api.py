import pytest

from app.models import *
from app.core import ErrorCode
from tests.utils.api_assertions import assert_response_error, assert_response_ok
from tests.utils.database import (
    role_user,
    user,
    auth_client,
    collection_factory,
    document_factory,
    user_factory,
    TEST_PASSWORD,
)


class TestCreateCollection:
    def test_success(self, auth_client):
        assert_response_ok(
            auth_client.post("/collections", json={"name": "New Collection"})
        )

    def test_unauthenticated(self, client):
        assert_response_error(
            client.post("/collections", json={"name": "New Collection"}),
            ErrorCode.UNAUTHORIZED,
        )

    def test_duplicate_name(self, user, db_session, auth_client):
        collection = Collection(name="New Collection", owner=user)
        db_session.add(collection)
        db_session.commit()

        assert_response_error(
            auth_client.post("/collections", json={"name": collection.name}),
            ErrorCode.RESOURCE_ALREADY_EXISTS,
        )

    def test_missing_name(self, auth_client):
        assert_response_error(
            auth_client.post("/collections"), ErrorCode.VALIDATION_ERROR
        )


class TestRenameCollection:
    def test_success(self, auth_client, user, collection_factory):
        collection = collection_factory.create(owner=user)
        assert_response_ok(
            auth_client.patch(
                f"/collections/{collection.id}", json={"new_name": "New Name"}
            ),
        )

    def test_collection_not_found(self, auth_client):
        assert_response_error(
            auth_client.patch(f"/collections/{1}", json={"new_name": "New Name"}),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

    def test_rename_to_existing_name(self, auth_client, user, collection_factory):
        collections = collection_factory.create_many(owner=user, n=2)
        assert_response_error(
            auth_client.patch(
                f"/collections/{collections[0].id}",
                json={"new_name": collections[1].name},
            ),
            ErrorCode.RESOURCE_ALREADY_EXISTS,
        )

    def test_stranger_cannot_rename(
        self, client, user, collection_factory, user_factory
    ):
        collection = collection_factory.create(owner=user)
        stranger = user_factory.create("stranger", "stranger@mail", TEST_PASSWORD)

        assert_response_ok(
            client.post(
                "/auth/login",
                json={"identity": stranger.username, "password": TEST_PASSWORD},
            )
        )

        assert_response_error(
            client.patch(
                f"/collections/{collection.id}", json={"new_name": "New Name"}
            ),
            ErrorCode.FORBIDDEN,
        )

    def test_unauthenticated(self, client, user, collection_factory):
        collection = collection_factory.create(owner=user)
        assert_response_error(
            client.patch(
                f"/collections/{collection.id}", json={"new_name": "New Name"}
            ),
            ErrorCode.UNAUTHORIZED,
        )

    def test_missing_field(self, auth_client, user, collection_factory):
        collection = collection_factory.create(owner=user)
        assert_response_error(
            auth_client.patch(f"/collections/{collection.id}"),
            ErrorCode.VALIDATION_ERROR,
        )


class TestDeleteCollection:
    def test_success(self, auth_client, user, collection_factory):
        collection = collection_factory.create(owner=user)
        assert_response_ok(auth_client.delete(f"/collections/{collection.id}"))

    def test_collection_not_found(self, auth_client):
        assert_response_error(
            auth_client.delete(f"/collections/{1}"),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

    def test_unauthenticated(self, client, user, collection_factory):
        collection = collection_factory.create(owner=user)
        assert_response_error(
            client.delete(f"/collections/{collection.id}"),
            ErrorCode.UNAUTHORIZED,
        )

    def test_stranger_cannot_delete(
        self, client, user, collection_factory, user_factory
    ):
        collection = collection_factory.create(owner=user)
        stranger = user_factory.create("stranger", "stranger@mail", TEST_PASSWORD)

        assert_response_ok(
            client.post(
                "/auth/login",
                json={"identity": stranger.username, "password": TEST_PASSWORD},
            )
        )
        assert_response_error(
            client.delete(f"/collections/{collection.id}"), ErrorCode.FORBIDDEN
        )


class TestAddDocumentToCollection:
    def test_add_self_public_document(
        self, auth_client, user, collection_factory, document_factory
    ):
        collection = collection_factory.create(owner=user)
        document = document_factory.create(
            owner=user, category=Category(name="Test Category")
        )
        assert_response_ok(
            auth_client.put(f"/collections/{collection.id}/items/{document.id}")
        )

    def test_add_self_private_document(
        self, auth_client, user, collection_factory, document_factory
    ):
        collection = collection_factory.create(owner=user)
        document = document_factory.create(
            owner=user,
            category=Category(name="Test Category"),
            visibility=DocumentVisibility.PRIVATE,
        )
        assert_response_ok(
            auth_client.put(f"/collections/{collection.id}/items/{document.id}")
        )

    def test_add_other_user_public_document(
        self, auth_client, user, collection_factory, document_factory, user_factory
    ):
        collection = collection_factory.create(owner=user)

        other_user = user_factory.create("other_user", "other_user@mail", TEST_PASSWORD)
        document = document_factory.create(
            owner=other_user, category=Category(name="Category")
        )

        assert_response_ok(
            auth_client.put(f"/collections/{collection.id}/items/{document.id}")
        )

    def test_add_other_user_private_document(
        self, auth_client, user, collection_factory, document_factory, user_factory
    ):
        collection = collection_factory.create(owner=user)

        other_user = user_factory.create("other_user", "other_user@mail", TEST_PASSWORD)
        document = document_factory.create(
            owner=other_user,
            category=Category(name="Category"),
            visibility=DocumentVisibility.PRIVATE,
        )

        assert_response_error(
            auth_client.put(f"/collections/{collection.id}/items/{document.id}"),
            ErrorCode.FORBIDDEN,
        )

    def test_collection_not_found(self, auth_client, user, document_factory):
        document = document_factory.create(
            owner=user, category=Category(name="Test Category")
        )
        assert_response_error(
            auth_client.put(f"/collections/{1}/items/{document.id}"),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

    def test_document_not_found(self, auth_client, user, collection_factory):
        collection = collection_factory.create(owner=user)
        assert_response_error(
            auth_client.put(f"/collections/{collection.id}/items/{1}"),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

    def test_stranger_cannot_add(
        self, client, user, collection_factory, document_factory, user_factory
    ):
        collection = collection_factory.create(owner=user)
        document = document_factory.create(
            owner=user, category=Category(name="Test Category")
        )

        stranger = user_factory.create("stranger", "stranger@mail", TEST_PASSWORD)

        assert_response_ok(
            client.post(
                "/auth/login",
                json={"identity": stranger.username, "password": TEST_PASSWORD},
            )
        )
        assert_response_error(
            client.put(f"/collections/{collection.id}/items/{document.id}"),
            ErrorCode.FORBIDDEN,
        )


class TestRemoveDocumentFromCollection:
    def test_success(self, auth_client, user, collection_factory, document_factory):
        collection = collection_factory.create(owner=user)
        document = document_factory.create(
            owner=user, category=Category(name="Test Category")
        )
        assert_response_ok(
            auth_client.delete(f"/collections/{collection.id}/items/{document.id}")
        )

    def test_collection_not_found(self, auth_client, user, document_factory):
        document = document_factory.create(
            owner=user, category=Category(name="Test Category")
        )
        assert_response_error(
            auth_client.delete(f"/collections/{1}/items/{document.id}"),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

    def test_document_not_found(self, auth_client, user, collection_factory):
        collection = collection_factory.create(owner=user)
        assert_response_error(
            auth_client.delete(f"/collections/{collection.id}/items/{1}"),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

    def test_stranger_cannot_remove(
        self, client, user, collection_factory, document_factory, user_factory
    ):
        collection = collection_factory.create(owner=user)
        document = document_factory.create(
            owner=user, category=Category(name="Test Category")
        )
        stranger = user_factory.create("stranger", "stranger@mail", TEST_PASSWORD)

        assert_response_ok(
            client.post(
                "/auth/login",
                json={"identity": stranger.username, "password": TEST_PASSWORD},
            )
        )

        assert_response_error(
            client.delete(f"/collections/{collection.id}/items/{document.id}"),
            ErrorCode.FORBIDDEN,
        )

    def test_unauthenticated(self, client, user, collection_factory, document_factory):
        collection = collection_factory.create(owner=user)
        document = document_factory.create(
            owner=user, category=Category(name="Test Category")
        )
        assert_response_error(
            client.delete(f"/collections/{collection.id}/items/{document.id}"),
            ErrorCode.UNAUTHORIZED,
        )


class TestGetCollectionItems:
    def test_success(self, auth_client, user, collection_factory, document_factory):
        documents = document_factory.create_many(
            n=100, owner=user, category=Category(name="Test Category")
        )
        collection = collection_factory.create(owner=user, items=documents)
        docs = assert_response_ok(
            auth_client.get(
                f"/collections/{collection.id}/items", params={"page": 1, "limit": 10}
            )
        )
        assert isinstance(docs, list)

    def test_collection_not_found(self, auth_client):
        assert_response_error(
            auth_client.get(f"/collections/{1}/items"), ErrorCode.RESOURCE_NOT_FOUND
        )

    def test_stranger_cannot_get(
        self, client, user, collection_factory, document_factory, user_factory
    ):
        documents = document_factory.create_many(
            n=10, owner=user, category=Category(name="Test Category")
        )
        collection = collection_factory.create(owner=user, items=documents)
        stranger = user_factory.create("stranger", "stranger@mail", TEST_PASSWORD)

        assert_response_ok(
            client.post(
                "/auth/login",
                json={"identity": stranger.username, "password": TEST_PASSWORD},
            )
        )
        assert_response_error(
            client.get(f"/collections/{collection.id}/items"), ErrorCode.FORBIDDEN
        )

    def test_unauthenticated(self, client, user, collection_factory, document_factory):
        documents = document_factory.create_many(
            n=100, owner=user, category=Category(name="Test Category")
        )
        collection = collection_factory.create(owner=user, items=documents)
        assert_response_error(
            client.get(
                f"/collections/{collection.id}/items", params={"page": 1, "limit": 10}
            ),
            ErrorCode.UNAUTHORIZED,
        )

    @pytest.mark.parametrize(
        ["page", "limit"],
        [
            [0, 10],
            [-1, 10],
            [1, -1],
            [1, 0],
            [1, 101],
        ],
    )
    def test_invalid_pagination_query(
        self, auth_client, user, collection_factory, document_factory, page, limit
    ):
        documents = document_factory.create_many(
            n=100, owner=user, category=Category(name="Test Category")
        )
        collection = collection_factory.create(owner=user, items=documents)
        assert_response_error(
            auth_client.get(
                f"/collections/{collection.id}/items",
                params={"page": page, "limit": limit},
            ),
            ErrorCode.VALIDATION_ERROR,
        )
