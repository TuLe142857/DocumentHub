import pytest
from pytest_mock import MockFixture

from app.core import ErrorCode, get_settings
from tests.utils.api_assertions import assert_response_error, assert_response_ok
from tests.utils.database import admin_client, auth_client, seeded_db


@pytest.fixture
def mock_otp(mocker: MockFixture):
    _otp = mocker.patch("app.services.auth_service.generate_otp")
    _otp.return_value = "otp_code"
    return _otp


@pytest.mark.parametrize(
    ["email", "username", "password"],
    [("fake_mail@mail.com", "some_user", "12345678")],
)
def test_registration_flow_success(client, email, username, password, mock_otp):
    """
    Flow test:

    -> Registration(Auto login after complete)
        -> Logout
            -> Login
                -> Refresh Access Token
                    -> Logout
                        -> Forgot Password
                            -> Reset Password
                                -> Login
    Args:
        client:
        email:
        username:
        password:
        mock_otp:

    Returns:

    """

    # registration
    assert_response_ok(client.post("auth/register/request", json={"email": email}))

    assert_response_ok(
        client.post(
            "/auth/register/verify",
            json={
                "email": email,
                "otp_code": "otp_code",
            },
        )
    )

    assert_response_ok(
        client.post(
            "/auth/register/complete",
            json={
                "email": email,
                "registration_code": "otp_code",
                "username": username,
                "password": password,
            },
        )
    )

    # check auto login after complete registration
    assert_response_ok(client.get("/auth/whoami"))

    # test logout
    assert_response_ok(client.post("/auth/logout"))
    assert_response_error(
        client.get("/auth/whoami"), expected_error=ErrorCode.UNAUTHORIZED
    )

    # test login by email
    assert_response_ok(
        client.post(
            "/auth/login",
            json={
                "identity": email,
                "password": password,
            },
        )
    )
    assert_response_ok(client.get("/auth/whoami"))

    # test login by username
    assert_response_ok(client.post("/auth/logout"))
    assert_response_ok(
        client.post(
            "/auth/login",
            json={
                "identity": username,
                "password": password,
            },
        )
    )
    assert_response_ok(client.get("/auth/whoami"))

    # test refresh access token
    assert_response_ok(client.post("/auth/refresh"))
    assert_response_ok(client.get("/auth/whoami"))

    # test forgot & reset password
    assert_response_ok(client.post("/auth/logout"))
    assert_response_ok(client.post("/auth/forgot_password", json={"identity": email}))
    assert_response_ok(
        client.post(
            "/auth/reset_password",
            json={
                "identity": email,
                "otp_code": "otp_code",
                "new_password": "new_password123",
            },
        )
    )
    assert_response_ok(
        client.post(
            "/auth/login",
            json={
                "identity": username,
                "password": "new_password123",
            },
        )
    )


def test_logout_api(auth_client):
    settings = get_settings()

    # get cookie before call logout
    access_cookie = auth_client.cookies.get(settings.JWT_ACCESS_COOKIE_NAME)
    refresh_cookie = auth_client.cookies.get(settings.JWT_REFRESH_COOKIE_NAME)
    assert access_cookie is not None
    assert refresh_cookie is not None

    # call logout, clear cookie and revoke jwt token
    assert_response_ok(auth_client.post("/auth/logout"))

    # set old jwt token to cookie and check after logout
    auth_client.cookies.set(settings.JWT_ACCESS_COOKIE_NAME, access_cookie)
    auth_client.cookies.set(settings.JWT_REFRESH_COOKIE_NAME, refresh_cookie)

    # check access token is revoked
    assert_response_error(
        auth_client.get("/auth/whoami"), expected_error=ErrorCode.JWT_TOKEN_REVOKED
    )

    # check refresh token is revoked
    assert_response_error(
        auth_client.post("/auth/refresh"), expected_error=ErrorCode.JWT_TOKEN_REVOKED
    )
