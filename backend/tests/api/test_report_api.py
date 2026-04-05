from tests.utils.api_assertions import assert_response_error, assert_response_ok
from tests.utils.db_fixture import (
    auth_client,
    category,
    collection,
    document,
    report_reasons,
    role_admin,
    role_user,
    user,
)


def test_get_available_report_reason(client, report_reasons):
    reasons = assert_response_ok(client.get("/reports/available_reasons"))
    assert isinstance(reasons, list)


def test_report_document_api_success(auth_client, report_reasons, document):
    assert_response_ok(
        auth_client.post(
            f"/reports/documents/{document.id}",
            json={"reason": report_reasons[0].id, "desc": "Description"},
        )
    )
