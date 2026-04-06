from tests.utils.api_assertions import assert_response_error, assert_response_ok
from tests.utils.database import auth_client, seeded_db


def test_get_self_profile_success(auth_client):
    assert_response_ok(auth_client.get("/users/me/profile"))


def test_get_self_documents_success(auth_client, seeded_db):
    user = seeded_db.user
    assert_response_ok(auth_client.get(f"/users/{user.username}/documents"))


def test_update_avatar_success(auth_client):
    assert_response_ok(
        auth_client.put(
            "/users/me/avatar", files={"avatar": ("avatar.png", b"fake binary content")}
        )
    )


def test_get_other_profile_success(client, seeded_db):
    user = seeded_db.user
    assert_response_ok(client.get(f"/users/{user.username}/profile"))


def test_get_other_documents_success(client, seeded_db):
    user = seeded_db.user
    assert_response_ok(client.get(f"/users/{user.username}/documents"))
