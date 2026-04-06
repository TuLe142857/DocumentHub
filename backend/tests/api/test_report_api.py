from tests.utils.api_assertions import assert_response_error, assert_response_ok
from tests.utils.database import auth_client, seeded_db


def test_get_available_report_reason(client, seeded_db):
    reasons = assert_response_ok(client.get("/reports/available_reasons"))
    assert isinstance(reasons, list)


def test_report_document_api_success(auth_client, seeded_db):
    document = seeded_db.public_document
    report_reasons = seeded_db.report_reasons
    assert_response_ok(
        auth_client.post(
            f"/reports/documents/{document.id}",
            json={"reason": report_reasons[0].id, "desc": "Description"},
        )
    )
