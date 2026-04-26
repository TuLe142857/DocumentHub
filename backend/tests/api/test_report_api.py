from tests.utils.api_assertions import assert_response_error, assert_response_ok
from tests.utils.database import auth_client, role_user, user


class TestGetAvailableReasons:
    def test_success(self, client):
        reasons = assert_response_ok(client.get("/reports/available_reasons"))
        assert isinstance(reasons, list)


class TestReportDocument:
    def test_success(self):
        pass

    def test_unauthenticated(self):
        pass

    def test_document_not_found(self):
        pass

    def test_invalid_reason(self):
        pass

    def test_user_already_reported_document(self):
        pass
