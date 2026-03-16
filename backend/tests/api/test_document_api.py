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

def test_update_document_api(client, user, document):
    assert True


