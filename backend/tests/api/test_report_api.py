from tests.utils.api_assertions import assert_response_error, assert_response_ok
from tests.utils.database import auth_client, role_user, user, report_reasons, category_factory, document_factory, \
    user_factory, TEST_PASSWORD
from app.models import *
from app.core import ErrorCode

class TestGetAvailableReasons:
    def test_success(self, client):
        reasons = assert_response_ok(client.get("/reports/available_reasons"))
        assert isinstance(reasons, list)


class TestReportDocument:
    def test_user_can_report_others_public_document(self, auth_client, user, document_factory, category_factory, report_reasons, user_factory):
        other_user = user_factory.create(username="other_user", email="other_user@mail", password=TEST_PASSWORD)
        other_public_doc = document_factory.create(owner=other_user, category=category_factory.create())

        assert_response_ok(
            auth_client.post(f"/reports/documents/{other_public_doc.id}", json={"desc": "report reason desc...", "reason": report_reasons[0].id})
        )

    def test_user_cannot_report_others_private_document(self, auth_client, user, document_factory, category_factory, report_reasons, user_factory):
        other_user = user_factory.create(username="other_user", email="other_user@mail", password=TEST_PASSWORD)
        other_private_doc = document_factory.create(owner=other_user, visibility=DocumentVisibility.PRIVATE, category=category_factory.create())

        assert_response_error(
            auth_client.post(f"/reports/documents/{other_private_doc.id}", json={"desc": "report reason desc...", "reason": report_reasons[0].id}),
            ErrorCode.FORBIDDEN
        )

    def test_unauthenticated(self, client, user, document_factory, category_factory, report_reasons):
        doc = document_factory.create(owner=user, category=category_factory.create())
        assert_response_error(
            client.post(f"/reports/documents/{doc.id}",
                             json={"desc": "report reason desc...", "reason": report_reasons[0].id}),
            ErrorCode.UNAUTHORIZED
        )

    def test_document_not_found(self, auth_client, report_reasons):
        assert_response_error(
            auth_client.post("/reports/documents/1", json={"desc": "report reason desc...", "reason": report_reasons[0].id}),
            ErrorCode.RESOURCE_NOT_FOUND
        )

    def test_invalid_reason(self, auth_client, user, document_factory, category_factory, user_factory):
        other_user = user_factory.create(username="other_user", email="other_user@mail", password=TEST_PASSWORD)
        other_public_doc = document_factory.create(owner=other_user, category=category_factory.create())

        assert_response_error(
            auth_client.post(f"/reports/documents/{other_public_doc.id}", json={"desc": "report reason desc...", "reason": 1}),
            ErrorCode.RESOURCE_NOT_FOUND
        )

    def test_user_already_reported_document(self, auth_client, user, document_factory, category_factory, report_reasons, user_factory):
        other_user = user_factory.create(username="other_user", email="other_user@mail", password=TEST_PASSWORD)
        other_public_doc = document_factory.create(owner=other_user, category=category_factory.create())

        assert_response_ok(
            auth_client.post(f"/reports/documents/{other_public_doc.id}", json={"desc": "report reason desc...", "reason": report_reasons[0].id})
        )

        assert_response_error(
            auth_client.post(f"/reports/documents/{other_public_doc.id}",
                             json={"desc": "report reason desc...", "reason": report_reasons[0].id}),
            ErrorCode.ACTION_ALREADY_PERFORMED
        )
