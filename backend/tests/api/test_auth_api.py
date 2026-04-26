import pytest
from pytest_mock import MockFixture

from app.core import ErrorCode, get_settings
from tests.utils.api_assertions import assert_response_error, assert_response_ok

from tests.utils.database import auth_client, role_user, user, TEST_PASSWORD


@pytest.fixture
def mock_otp(mocker: MockFixture):
    _otp = mocker.patch("app.services.auth_service.generate_otp")
    _otp.return_value = "otp_code"
    return "otp_code"


REGISTRATION_EMAIL = "register@faketestl.com"
REGISTRATION_USERNAME = "register_username"


class TestRegisterRequest:
    def test_success(self, client):
        assert_response_ok(
            client.post("/auth/register/request", json={"email": REGISTRATION_EMAIL})
        )

    def test_email_already_exists(self, client, user):
        assert_response_error(
            client.post("/auth/register/request", json={"email": user.email}),
            ErrorCode.RESOURCE_ALREADY_EXISTS,
        )

    @pytest.mark.parametrize("email", ["", "mail"])
    def test_invalid_email_format(self, client, email):
        assert_response_error(
            client.post("/auth/register/request", json={"email": email}),
            ErrorCode.VALIDATION_ERROR,
        )

    def test_missing_email_field(self, client):
        assert_response_error(
            client.post("/auth/register/request"),
        )


class TestRegisterVerify:
    def test_success(self, client, mock_otp):
        client.post("/auth/register/request", json={"email": REGISTRATION_EMAIL})
        res_data = assert_response_ok(
            client.post(
                "/auth/register/verify",
                json={"email": REGISTRATION_EMAIL, "otp_code": mock_otp},
            )
        )
        assert "registration_code" in res_data

    def test_wrong_otp(self, client, mock_otp):
        client.post("/auth/register/request", json={"email": REGISTRATION_EMAIL})
        assert_response_error(
            client.post(
                "/auth/register/verify",
                json={"email": REGISTRATION_EMAIL, "otp_code": "fake_otp"},
            ),
            ErrorCode.INVALID_CODE,
        )

    @pytest.mark.parametrize(
        "body",
        [
            {"email": REGISTRATION_EMAIL},
            {"otp_code": "fake_otp"},
        ],
    )
    def test_missing_field(self, client, mock_otp, body):
        client.post("/auth/register/request", json={"email": REGISTRATION_EMAIL})
        assert_response_error(
            client.post(
                "/auth/register/verify",
                json=body,
            ),
            ErrorCode.VALIDATION_ERROR,
        )


class TestRegisterComplete:
    @staticmethod
    def _do_register(client, mock_otp, email):
        client.post("/auth/register/request", json={"email": email})
        client.post(
            "/auth/register/verify", json={"otp_code": mock_otp, "email": email}
        )

    def test_success(self, client, mock_otp):
        self._do_register(client, mock_otp, REGISTRATION_EMAIL)

        res_data = assert_response_ok(
            client.post(
                "/auth/register/complete",
                json={
                    "email": REGISTRATION_EMAIL,
                    "username": REGISTRATION_USERNAME,
                    "password": "password_123",
                    "registration_code": mock_otp,
                },
            )
        )

        # check return access/refresh token
        # use for mobile client
        assert "access_token" in res_data
        assert "refresh_token" in res_data

        # check auto login(auto set jwt cookie)
        # use for web client
        assert_response_ok(client.get("/auth/whoami"))

    def test_invalid_registration_code(self, client, mock_otp):
        self._do_register(client, mock_otp, REGISTRATION_EMAIL)
        assert_response_error(
            client.post(
                "/auth/register/complete",
                json={
                    "email": REGISTRATION_EMAIL,
                    "username": REGISTRATION_USERNAME,
                    "password": "password_123",
                    "registration_code": "fake_otp",
                },
            ),
            ErrorCode.INVALID_CODE,
        )

    def test_username_already_exists(self, client, mock_otp, user):
        self._do_register(client, mock_otp, REGISTRATION_EMAIL)
        assert_response_error(
            client.post(
                "/auth/register/complete",
                json={
                    "email": REGISTRATION_EMAIL,
                    "username": user.username,
                    "password": "password_123",
                    "registration_code": mock_otp,
                },
            ),
            ErrorCode.RESOURCE_ALREADY_EXISTS,
        )

    @pytest.mark.parametrize("password", ["0", "000", "0000000"])
    def test_invalid_password(self, client, mock_otp, password):
        self._do_register(client, mock_otp, REGISTRATION_EMAIL)
        assert_response_error(
            client.post(
                "/auth/register/complete",
                json={
                    "email": REGISTRATION_EMAIL,
                    "username": REGISTRATION_USERNAME,
                    "password": password,
                    "registration_code": mock_otp,
                },
            ),
            ErrorCode.VALIDATION_ERROR,
        )


class TestLogin:
    def test_login_by_email_success(self, client, user):
        assert_response_ok(
            client.post(
                "/auth/login",
                json={
                    "identity": user.email,
                    "password": TEST_PASSWORD,
                },
            )
        )

    def test_login_by_username_success(self, client, user):
        assert_response_ok(
            client.post(
                "/auth/login",
                json={
                    "identity": user.username,
                    "password": TEST_PASSWORD,
                },
            )
        )

    def test_wrong_password(self, client, user):
        assert_response_error(
            client.post(
                "/auth/login",
                json={
                    "identity": user.username,
                    "password": TEST_PASSWORD + "fake",
                },
            ),
            ErrorCode.LOGIN_FAILED,
        )

    def test_nonexistent_identity(self, client):
        assert_response_error(
            client.post(
                "/auth/login",
                json={
                    "identity": "noneuser",
                    "password": "password678",
                },
            ),
            ErrorCode.LOGIN_FAILED,
        )

    def test_banned_user(self, client, user, db_session):
        user.is_active = False
        db_session.commit()

        assert_response_error(
            client.post(
                "/auth/login",
                json={
                    "identity": user.username,
                    "password": TEST_PASSWORD,
                },
            ),
            ErrorCode.USER_INACTIVE,
        )

    @pytest.mark.parametrize(
        "body",
        [
            {"identity": "identity"},
            {"password": "password"},
        ],
    )
    def test_missing_field(self, client, body):
        assert_response_error(
            client.post("/auth/login", json=body), ErrorCode.VALIDATION_ERROR
        )


class TestWhoami:
    def test_authenticated_cookie(self, auth_client):
        assert_response_ok(auth_client.get("/auth/whoami"))

    def test_unauthenticated(self, client):
        assert_response_error(client.get("/auth/whoami"), ErrorCode.UNAUTHORIZED)

    def test_banned_user(self, auth_client, user, db_session):
        user.is_active = False
        db_session.commit()
        assert_response_error(auth_client.get("/auth/whoami"), ErrorCode.USER_INACTIVE)


class TestLogout:
    def test_success(self, client, user):
        login_response = (
            client.post(
                "/auth/login",
                json={
                    "identity": user.username,
                    "password": TEST_PASSWORD,
                },
            )
            .json()
            .get("data")
        )
        access_token = login_response.get("access_token")
        refresh_token = login_response.get("refresh_token")

        # call logout
        assert_response_ok(client.post("/auth/logout"))

        # test jwt token revoked after logout
        settings = get_settings()
        client.cookies.set(settings.JWT_ACCESS_COOKIE_NAME, access_token)
        client.cookies.set(settings.JWT_REFRESH_COOKIE_NAME, refresh_token)

        assert_response_error(client.get("/auth/whoami"), ErrorCode.JWT_TOKEN_REVOKED)

        assert_response_error(client.post("/auth/refresh"), ErrorCode.JWT_TOKEN_REVOKED)


class TestRefreshAccessToken:
    def test_success(self, client, user):
        client.post(
            "/auth/login",
            json={
                "identity": user.username,
                "password": TEST_PASSWORD,
            },
        )

        # delete access cookie to test refresh
        settings = get_settings()
        client.cookies.delete(settings.JWT_ACCESS_COOKIE_NAME)

        assert_response_error(client.get("/auth/whoami"), ErrorCode.UNAUTHORIZED)

        # call refresh api
        assert_response_ok(client.post("/auth/refresh"))
        assert_response_ok(client.get("/auth/whoami"))

    def test_refresh_with_fake_token(self, client):
        settings = get_settings()
        client.cookies.set(settings.JWT_REFRESH_COOKIE_NAME, "fake_jwt_token")
        assert_response_error(client.post("/auth/refresh"), ErrorCode.INVALID_JWT_TOKEN)


class TestForgotPassword:
    def test_success(self, client, user):
        assert_response_ok(
            client.post("/auth/forgot_password", json={"identity": user.email})
        )

    def test_nonexistent_identity(self, client):
        assert_response_error(
            client.post("/auth/forgot_password", json={"identity": "nonuser"}),
            ErrorCode.INVALID_CREDENTIALS,
        )

    def test_missing_field(self, client):
        assert_response_error(
            client.post("/auth/forgot_password"), ErrorCode.VALIDATION_ERROR
        )


class TestResetPassword:
    @pytest.mark.parametrize("new_password", ["password123", "1234567890"])
    def test_success(self, client, mock_otp, user, new_password):
        client.post("/auth/forgot_password", json={"identity": user.email})
        assert_response_ok(
            client.post(
                "/auth/reset_password",
                json={
                    "identity": user.email,
                    "otp_code": mock_otp,
                    "new_password": new_password,
                },
            )
        )

    def test_wrong_otp(self, client, mock_otp, user):
        client.post("/auth/forgot_password", json={"identity": user.email})
        assert_response_error(
            client.post(
                "/auth/reset_password",
                json={
                    "identity": user.email,
                    "otp_code": mock_otp + "fake",
                    "new_password": "password123",
                },
            ),
            ErrorCode.INVALID_CODE,
        )

    @pytest.mark.parametrize("new_password", ["", "p", "1234567"])
    def test_invalid_password(self, client, mock_otp, user, new_password):
        client.post("/auth/forgot_password", json={"identity": user.email})
        assert_response_error(
            client.post(
                "/auth/reset_password",
                json={
                    "identity": user.email,
                    "otp_code": mock_otp,
                    "new_password": new_password,
                },
            ),
            ErrorCode.VALIDATION_ERROR,
        )
