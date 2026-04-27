import pytest

from app.core import ErrorCode
from app.models import *
from tests.utils.api_assertions import assert_response_error, assert_response_ok
from tests.utils.database import  role_user, user, auth_client, document_factory, category_factory, collection_factory

class TestGetSelfProfile:
    def test_success(self, auth_client):
        profile = assert_response_ok(auth_client.get("/users/me/profile"))
        required_fields = ["username", "avatar_url", "full_name", "gender", "phone_number", "bio"]
        assert all(f in profile for f in required_fields)

    def test_unauthenticated(self, client):
        assert_response_error(client.get("/users/me/profile"), ErrorCode.UNAUTHORIZED)


class TestUpdateSelfProfile:
    @pytest.mark.parametrize("body",
        [
            {
                "full_name": "new full name",
                "gender": Gender.MALE.value,
                "phone_number": "09374212",
                "bio": "new bio"
            }
        ]
    )
    def test_success(self, auth_client, body:dict):
        assert_response_ok(auth_client.patch("/users/me/profile", json=body))

        # check after update
        profile_after_update = assert_response_ok(auth_client.get("/users/me/profile"))
        for key, value in body.items():
            assert profile_after_update.get(key) == value

    def test_unauthenticated(self, client):
        assert_response_error(client.patch("/users/me/profile", json={"full_name": "new full name"}), ErrorCode.UNAUTHORIZED)

    @pytest.mark.parametrize("body",
         [
             {
                 "gender": "wrong gender",
             }
         ]
     )
    def test_validation_error(self, auth_client,  body):
        assert_response_error(
            auth_client.patch("/users/me/profile", json=body),
            ErrorCode.VALIDATION_ERROR
        )


class TestUpdateAvatar:
    def test_success(self, auth_client):
        with open("tests/files/avatar.jpg", "rb") as f:
            assert_response_ok(
                auth_client.put("/users/me/avatar", files={"avatar": ("avatar.jpg", f)}),
            )

    def test_unauthenticated(self, client):
        with open("tests/files/avatar.jpg", "rb") as f:
            assert_response_error(
                client.put("/users/me/avatar", files={"avatar": ("avatar.jpg", f)}),
                ErrorCode.UNAUTHORIZED
            )

    @pytest.mark.parametrize("filename", [".ico", ".svg", ".pdf"])
    def test_invalid_avatar_type(self, auth_client, filename):
        assert_response_error(
            auth_client.put("/users/me/avatar", files={"avatar": (filename, b'fake binary')}),
            ErrorCode.UNSUPPORTED_FILE_TYPE
        )


class TestGetSelfDocuments:

    def test_success(self, user, auth_client, document_factory, category_factory):
        documents = document_factory.create_many(n=200, owner=user, category=category_factory.create())

        assert_response_ok(
            auth_client.get("/users/me/documents"),
        )

    def test_unauthenticated(self, client):
        assert_response_error(client.get("/users/me/documents"), ErrorCode.UNAUTHORIZED)


class TestGetSelfCollections:
    def test_success(self, user, auth_client, collection_factory):
        collections = collection_factory.create_many(n=200, owner=user)
        assert_response_ok(
            auth_client.get("/users/me/collections"),
        )

    def test_unauthenticated(self, client):
        assert_response_error(
            client.get("/users/me/collections"),
            ErrorCode.UNAUTHORIZED
        )


class TestGetLikedDocuments:
    def test_success(self, auth_client):
        assert_response_ok(
            auth_client.get("/users/me/liked_documents"),
        )

    def test_unauthenticated(self, client):
        assert_response_error(
            client.get("/users/me/liked_documents"),
            ErrorCode.UNAUTHORIZED
        )


class TestGetOtherUserProfile:
    def test_success(self, client, user):
        assert_response_ok(client.get(f"/users/{user.username}/profile"))

    def test_user_not_found(self, client):
        assert_response_error(
            client.get(f"/users/{"username_fake"}/profile"),
            ErrorCode.RESOURCE_NOT_FOUND
        )


class TestGetOtherUserDocuments:
    def test_success(self, client, user, document_factory, category_factory):
        documents = document_factory.create_many(n=200, owner=user, category=category_factory.create())
        assert_response_ok(
            client.get(f"/users/{user.username}/documents"),
        )

    def test_user_not_found(self, client):
        assert_response_error(
            client.get(f"/users/{"username_fake"}/documents"),
            ErrorCode.RESOURCE_NOT_FOUND
        )
