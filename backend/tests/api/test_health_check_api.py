from tests.utils.api_assertions import assert_response_ok


def test_health_check(client):
    assert_response_ok(client.get("/api/health"))
