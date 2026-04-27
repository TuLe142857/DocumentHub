from app.core import ErrorCode
from app.models import Category
from tests.utils.api_assertions import assert_response_error, assert_response_ok
from tests.utils.database import role_user, user, auth_client

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
    def test_regular_user_forbidden(self, auth_client, method, path):
        assert_response_error(
            auth_client.request(method, path),
            ErrorCode.FORBIDDEN,
        )


class TestAdminUserManagement:
    pass


class TestAdminDocumentManagement:
    pass


class TestAdminCategoryManagement:
    pass


class TestAdminReportManagement:
    pass
