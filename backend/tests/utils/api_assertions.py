import json
from typing import Any

from httpx import Response
import pytest

from app.core import ErrorCode


def _get_json_payload(response: Response, print_payload: bool = True) -> dict[str, Any]:
    try:
        payload = response.json()
        if print_payload:
            print("request: ", response.request)
            print("response: ", json.dumps(payload, indent=2), end="\n\n")
        return payload
    except:
        pytest.fail(
            f"Response is not valid JSON. Status: {response.status_code}, Body: {response.text}"
        )


def assert_response_ok(
    response: Response, expected_status_code: int = 200, print_payload: bool = True
) -> Any:
    """
    Helper function for asserting the response in case of success.
    Args:
        print_payload: print response payload (JSON) to stdout.
        response: Response object from TestClient.
        expected_status_code: expected http status code.

    Returns:
        response.json().get("data") for next test

    """

    payload = _get_json_payload(response, print_payload=print_payload)

    assert response.status_code == expected_status_code
    assert payload.get("success") is True
    assert "message" in payload
    assert "data" in payload
    return payload.get("data")


def assert_response_error(
    response: Response,
    expected_error: ErrorCode | None = None,
    print_payload: bool = True,
):
    """
    Helper function for asserting the response in case of failure.
    Args:
        response: Response object from TestClient.

        expected_error: expected ErrorCode or None.

            - If expected_error is None, this method will check response.status_code != 2xx.
            - If expected_error is not None, this method will check response.status_code == expected_error.status_code
        and response.json().get("error_code") == expected_error.error_code

        print_payload: print response payload (JSON) to stdout.

    Returns:
        None
    """

    payload = _get_json_payload(response, print_payload=print_payload)

    assert response.json().get("success") is False
    assert "message" in payload
    assert "error_code" in payload
    if expected_error is not None:
        assert response.status_code == expected_error.status_code
        assert payload.get("error_code") == expected_error.error_code
    else:
        # status code != 2xx
        assert (response.status_code // 100) != 2
