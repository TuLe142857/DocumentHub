from fastapi.testclient import TestClient

from tests.utils.api_assertions import assert_response_ok


def test_health_check(app):
    with TestClient(app) as client:
        assert_response_ok(client.get("/health"))
