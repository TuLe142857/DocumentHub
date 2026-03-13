import pytest
from pytest_mock import MockFixture

from tests.utils.api_assertions import *


@pytest.fixture
def mock_otp(mocker: MockFixture):
    _otp = mocker.patch("app.services.auth_service.generate_otp")
    _otp.return_value = "otp_code"
    return _otp


@pytest.mark.parametrize(
    "email, username, password",
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
    assert_response_ok(client.post("/api/auth/register/request", json={"email": email}))

    assert_response_ok(
        client.post(
            "/api/auth/register/verify",
            json={
                "email": email,
                "otp_code": "otp_code",
            },
        )
    )

    assert_response_ok(
        client.post(
            "/api/auth/register/complete",
            json={
                "email": email,
                "registration_code": "otp_code",
                "username": username,
                "password": password,
            },
        )
    )

    # check auto login after complete registration
    assert_response_ok(client.get("/api/auth/whoami"))

    # test logout
    assert_response_ok(client.post("/api/auth/logout"))
    assert_response_error(
        client.get("/api/auth/whoami"), expected_error=ErrorCode.UNAUTHORIZED
    )

    # test login by email
    assert_response_ok(
        client.post(
            "/api/auth/login",
            json={
                "identity": email,
                "password": password,
            },
        )
    )
    assert_response_ok(client.get("/api/auth/whoami"))

    # test login by username
    assert_response_ok(client.post("/api/auth/logout"))
    assert_response_ok(
        client.post(
            "/api/auth/login",
            json={
                "identity": username,
                "password": password,
            },
        )
    )
    assert_response_ok(client.get("/api/auth/whoami"))

    # test refresh access token
    assert_response_ok(client.post("/api/auth/refresh"))
    assert_response_ok(client.get("/api/auth/whoami"))

    # test forgot & reset password
    assert_response_ok(client.post("/api/auth/logout"))
    assert_response_ok(
        client.post("/api/auth/forgot_password", json={"identity": email})
    )
    assert_response_ok(
        client.post(
            "/api/auth/reset_password",
            json={
                "identity": email,
                "otp_code": "otp_code",
                "new_password": "new_password123",
            },
        )
    )
    assert_response_ok(
        client.post(
            "/api/auth/login",
            json={
                "identity": username,
                "password": "new_password123",
            },
        )
    )
