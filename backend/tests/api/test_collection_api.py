from app.models import *
from tests.utils.api_assertions import assert_response_error, assert_response_ok
from tests.utils.database import role_user, user, auth_client


class TestCreateCollection:
    def test_success(self, auth_client):
        assert_response_ok(
            auth_client.post("/collections", json={"name": "Test Create Collection"})
        )

    def test_unauthenticated(self, client):
        pass

    def test_duplicate_name(self, auth_client):
        pass

    def test_missing_name(self):
        pass


class TestRenameCollection:
    def test_success(self):
        pass

    def test_collection_not_found(self):
        pass

    def test_rename_to_existing_name(self):
        pass

    def test_stranger_cannot_rename(self):
        pass

    def test_unauthenticated(self):
        pass

    def test_missing_field(self):
        pass


class TestDeleteCollection:
    def test_success(self):
        pass

    def test_collection_not_found(self):
        pass

    def test_unauthenticated(self):
        pass

    def test_stranger_cannot_delete(self):
        pass


class TestAddDocumentToCollection:
    def test_success(self):
        pass

    def test_collection_not_found(self):
        pass

    def test_document_not_found(self):
        pass

    def test_stranger_cannot_add(self):
        pass

    def test_cannot_add_private_document_of_other_users(self):
        pass

    def test_missing_field(self):
        pass


class TestRemoveDocumentFromCollection:
    def test_success(self):
        pass

    def test_collection_not_found(self):
        pass

    def test_document_not_found(self):
        pass

    def test_stranger_cannot_remove(self):
        pass

    def test_unauthenticated(self):
        pass

    def test_missing_field(self):
        pass


class TestGetCollectionItems:
    def test_success(self):
        pass

    def test_collection_not_found(self):
        pass

    def test_stranger_cannot_get(self):
        pass

    def test_unauthenticated(self):
        pass

    def test_invalid_pagination_query(self):
        pass
