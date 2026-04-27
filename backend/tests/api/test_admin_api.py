from app.core import ErrorCode
from app.models import *
from tests.utils.api_assertions import (
    assert_response_error,
    assert_response_ok,
    assert_response_paginated_ok,
)
from tests.utils.database import (
    role_user,
    user,
    auth_client,
    role_admin,
    admin,
    admin_client,
    user_factory,
    document_factory,
    category_factory,
    report_factory,
    report_reasons,
)
import dataclasses
import pytest


class TestAdminAuthorization:
    @pytest.mark.parametrize(
        "method,path",
        [
            ("GET", "/admin/users"),
            ("POST", "/admin/users/1/ban"),
            ("POST", "/admin/users/1/unban"),
            ("GET", "/admin/documents"),
            ("GET", "/admin/documents/1"),
            ("POST", "/admin/documents/1/unban"),
            ("POST", "/admin/categories"),
            ("PATCH", "/admin/categories/1"),
            ("DELETE", "/admin/categories/1"),
            ("GET", "/admin/reports"),
            ("GET", "/admin/reports/documents/1"),
            ("POST", "/admin/reports/documents/1"),
        ],
    )
    def test_regular_user_forbidden(self, auth_client, client, method, path):
        assert_response_error(
            auth_client.request(method, path),
            ErrorCode.FORBIDDEN,
        )

        assert_response_error(
            client.request(method, path),
            ErrorCode.UNAUTHORIZED,
        )


class TestAdminUserManagement:
    """
    ---------------------------------------
        GET /admin/users
    ---------------------------------------
    """

    @pytest.mark.parametrize(
        "query",
        [
            {
                "page": 1,
                "limit": 10,
            },
            {
                "page": 1,
                "limit": 10,
                "is_active": True,
            },
            {
                "page": 1,
                "limit": 10,
                "is_active": False,
            },
            {
                "page": 1,
                "limit": 10,
                "username": "user",
            },
            {
                "page": 1,
                "limit": 10,
                "email": "email",
            },
            {
                "page": 1,
                "limit": 10,
                "username": "user",
                "email": "email",
                "is_active": True,
            },
        ],
    )
    def test_get_user(self, db_session, admin_client, query, user_factory):
        users = user_factory.create_many(n=20)
        for i in range(10):
            users[i].is_active = False
        db_session.commit()

        response = assert_response_paginated_ok(
            admin_client.get("/admin/users", params=query),
            expected_page=query["page"],
            expected_limit=query["limit"],
        )
        assert isinstance(response, list)

        if "is_active" in query:
            assert all(item.get("is_active") == query["is_active"] for item in response)

    """
    ---------------------------------------
        POST /admin/users/{user_id}/ban
    ---------------------------------------
    """

    def test_ban_user_success(self, admin_client, user, auth_client):
        assert_response_ok(
            admin_client.post(f"/admin/users/{user.id}/ban", json={"reason": "..."}),
        )
        assert_response_error(auth_client.get("/auth/whoami"), ErrorCode.USER_INACTIVE)

    def test_ban_unactive_user(self, admin_client, user, auth_client):
        # ban user
        assert_response_ok(
            admin_client.post(f"/admin/users/{user.id}/ban", json={"reason": "..."}),
        )
        assert_response_error(auth_client.get("/auth/whoami"), ErrorCode.USER_INACTIVE)

        # ban user again
        assert_response_ok(
            admin_client.post(f"/admin/users/{user.id}/ban", json={"reason": "..."}),
        )

    def test_ban_user_notfound(self, admin_client):
        assert_response_error(
            admin_client.post("/admin/users/99999/ban", json={"reason": "..."}),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

    """
    ---------------------------------------
        POST /admin/users/{user_id}/unban
    ---------------------------------------
    """

    def test_unban_user_success(self, admin_client, user, auth_client):
        # ban user
        assert_response_ok(
            admin_client.post(f"/admin/users/{user.id}/ban", json={"reason": "..."}),
        )
        assert_response_error(auth_client.get("/auth/whoami"), ErrorCode.USER_INACTIVE)

        # unban user
        assert_response_ok(
            admin_client.post(f"/admin/users/{user.id}/unban"),
        )
        assert_response_ok(
            auth_client.get("/auth/whoami"),
        )

    def test_unban_active_user(self, admin_client, user, auth_client):
        # make sure user is active
        assert_response_ok(
            auth_client.get("/auth/whoami"),
        )

        # call api unban an active user
        assert_response_ok(
            admin_client.post(f"/admin/users/{user.id}/unban"),
        )

    def test_unban_user_notfound(self, admin_client):
        assert_response_error(
            admin_client.post("/admin/users/99999/unban"), ErrorCode.RESOURCE_NOT_FOUND
        )


class TestAdminDocumentManagement:
    """
    ---------------------------------------
        GET /admin/documents
    - List document with pagination
    ---------------------------------------
    """

    @pytest.mark.parametrize(
        "query",
        [
            {
                "page": 1,
                "limit": 10,
            }
        ],
    )
    def test_list_document(self, admin_client, query):
        assert_response_ok(
            admin_client.get("/admin/documents", params=query),
        )

    """
    ---------------------------------------
        GET /admin/documents/{document_id}
    - View document
    - Admin can access private document
    ---------------------------------------
    """

    def test_admin_can_get_public_document(
        self, admin_client, user, document_factory, category_factory
    ):
        category = category_factory.create()
        document = document_factory.create(owner=user, category=category)
        assert_response_ok(admin_client.get(f"/admin/documents/{document.id}"))

    def test_admin_can_get_private_document(
        self, admin_client, user, document_factory, category_factory
    ):
        category = category_factory.create()
        private_doc = document_factory.create(
            owner=user, category=category, visibility=DocumentVisibility.PRIVATE
        )
        assert_response_ok(admin_client.get(f"/admin/documents/{private_doc.id}"))

    """
    ---------------------------------------
        POST /admin/documents/{id}/unban
    - Unban document
    (document can only be banned when admin
    process reports)
    ---------------------------------------
    """

    def test_admin_unban_document(
        self, admin_client, user, document_factory, category_factory
    ):
        category = category_factory.create()
        private_doc = document_factory.create(
            owner=user,
            category=category,
            visibility=DocumentVisibility.PRIVATE,
            status=DocumentStatus.BANNED,
        )

        assert_response_ok(
            admin_client.post(f"/admin/documents/{private_doc.id}/unban")
        )

        # check document is active after unban
        response = assert_response_ok(
            admin_client.get(f"/admin/documents/{private_doc.id}"),
        )
        assert response.get("status") == DocumentStatus.READY.value


class TestAdminCategoryManagement:
    def test_create_category(self, admin_client, client):
        assert_response_ok(
            admin_client.post("/admin/categories", json={"name": "test"}),
        )

        # check category created
        response = assert_response_ok(client.get("/categories"))
        assert any(cat.get("name") == "test" for cat in response)

    def test_create_category_with_existed_name(self, admin_client, category_factory):
        category = category_factory.create(name="Category")
        assert_response_error(
            admin_client.post("/admin/categories", json={"name": category.name}),
            ErrorCode.RESOURCE_ALREADY_EXISTS,
        )

    def test_rename_category_success(self, admin_client, category_factory):
        category = category_factory.create(name="Category")
        assert_response_ok(
            admin_client.patch(
                f"/admin/categories/{category.id}", json={"new_name": "new_name"}
            ),
        )

        response = assert_response_ok(admin_client.get("/categories"))
        assert any(
            cat.get("name") == "new_name" and cat.get("id") == category.id
            for cat in response
        )

    def test_rename_category_with_existed_name(self, admin_client, category_factory):
        categories = category_factory.create_many(n=2)
        assert_response_error(
            admin_client.patch(
                f"/admin/categories/{categories[0].id}",
                json={"new_name": categories[1].name},
            ),
            ErrorCode.RESOURCE_ALREADY_EXISTS,
        )

    def test_delete_category_success(self, admin_client, category_factory):
        category = category_factory.create(name="Category")
        assert_response_ok(
            admin_client.delete(f"/admin/categories/{category.id}"),
        )

        response = assert_response_ok(admin_client.get("/categories"))
        assert all(cat.get("id") != category.id for cat in response)

    def test_delete_used_category(
        self, admin_client, category_factory, document_factory, user
    ):
        category = category_factory.create(name="Category")
        document = document_factory.create(owner=user, category=category)

        assert_response_error(
            admin_client.delete(f"/admin/categories/{category.id}"),
            ErrorCode.RESOURCE_IN_USE,
        )


class TestAdminReportManagement:
    """
    CUSTOM FIXTURE
    """

    @dataclasses.dataclass
    class ReportScenario:
        owners: list[User]
        documents: list[Document]
        reporters: list[User]
        doc_reports: list[DocumentReport]

    @pytest.fixture
    def report_scenario(
        self,
        category_factory,
        user_factory,
        document_factory,
        report_factory,
        report_reasons,
    ):
        owners = user_factory.create_many(
            n=5, username_prefix="owner_", email_prefix="owner_email_"
        )
        category = category_factory.create("ReportedDocCategory")
        documents = [
            document_factory.create(
                owner=owner, category=category, title=f"document of {owner.username}"
            )
            for owner in owners
        ]
        reporters = user_factory.create_many(
            n=10, username_prefix="reporter_", email_prefix="reporter_email_"
        )
        doc_reports = []
        for doc in documents:
            doc_reports += [
                report_factory.create_many(
                    document=doc, reporters=reporters, reasons=report_reasons
                )
            ]
        return TestAdminReportManagement.ReportScenario(
            owners=owners,
            documents=documents,
            reporters=reporters,
            doc_reports=doc_reports,
        )

    """
    ---------------------------------------
        GET /admin/reports
    - Get list of pending reported documents
    ---------------------------------------
    """

    def test_get_reported_documents(self, admin_client, report_scenario):
        assert_response_ok(admin_client.get(f"/admin/reports"))

    """
    ---------------------------------------
        GET /admin/reports/documents/{document_id}
    - Get list of reports of documents
    ---------------------------------------
    """

    def test_get_reports_of_document(self, admin_client, report_scenario):
        doc = report_scenario.documents[0]
        assert_response_ok(admin_client.get(f"/admin/reports/documents/{doc.id}"))

    def test_get_reported_documents_returns_empty_when_no_reports(
        self, admin_client, report_scenario, user, document_factory, category_factory
    ):
        category = category_factory.create(name="Category")
        document = document_factory.create(owner=user, category=category)

        response = assert_response_ok(
            admin_client.get(f"/admin/reports/documents/{document.id}")
        )
        assert isinstance(response, list)
        assert len(response) == 0

    def test_get_reports_of_document_document_not_found(self, admin_client):
        response = assert_response_error(
            admin_client.get(f"/admin/reports/documents/{9999}"),
            ErrorCode.RESOURCE_NOT_FOUND,
        )

    """
    ---------------------------------------
        POST /admin/reports/documents/{id}
    - Process all pending reports of document
    ---------------------------------------
    """

    def test_accept_reports_ban_document(self, admin_client, report_scenario):
        doc = report_scenario.documents[0]
        assert_response_ok(
            admin_client.post(
                f"/admin/reports/documents/{doc.id}",
                json={"accept": True, "note": "..."},
            )
        )

        # check document status == BANNED
        res = assert_response_ok(admin_client.get(f"/admin/documents/{doc.id}"))
        assert res.get("status") == DocumentStatus.BANNED.value

    def test_reject_reports_document_still_accessible(
        self, admin_client, report_scenario
    ):
        doc = report_scenario.documents[0]
        assert_response_ok(
            admin_client.post(
                f"/admin/reports/documents/{doc.id}",
                json={"accept": False, "note": "..."},
            )
        )

        # check document status still active
        res = assert_response_ok(admin_client.get(f"/admin/documents/{doc.id}"))
        assert res.get("status") == DocumentStatus.READY.value

    def test_process_reports_document_not_found(self, admin_client):
        assert_response_error(
            admin_client.post(
                f"/admin/reports/documents/{9999}",
                json={"accept": False, "note": "..."},
            ),
            ErrorCode.RESOURCE_NOT_FOUND,
        )
