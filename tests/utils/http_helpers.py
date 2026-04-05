"""HTTP request helper functions."""

from typing import Any

import requests


def make_request(
    session: requests.Session,
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    json_data: dict[str, Any] | None = None,
    data: dict[str, Any] | None = None,
    timeout: int = 30,
    expected_status: int | list[int] | None = None,
) -> requests.Response:
    """Make an HTTP request with common error handling.

    Args:
        session: Requests session
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        headers: Optional headers
        json_data: Optional JSON body
        data: Optional form data
        timeout: Request timeout in seconds
        expected_status: Expected status code(s), raises if not matched

    Returns:
        Response object

    Raises:
        AssertionError: If expected_status is set and doesn't match
        requests.RequestException: On request failure
    """
    response = session.request(
        method=method,
        url=url,
        headers=headers,
        json=json_data,
        data=data,
        timeout=timeout,
    )

    if expected_status is not None:
        if isinstance(expected_status, int):
            expected_status = [expected_status]
        assert response.status_code in expected_status, (
            f"Expected status {expected_status}, got {response.status_code}: {response.text}"
        )

    return response


def check_health(
    session: requests.Session,
    url: str,
    timeout: int = 30,
) -> tuple[bool, str]:
    """Check if a health endpoint is responding.

    Args:
        session: Requests session
        url: Health endpoint URL
        timeout: Request timeout in seconds

    Returns:
        Tuple of (is_healthy, message)
    """
    try:
        response = session.get(url, timeout=timeout)
        if response.status_code == 200:
            return True, "Healthy"
        else:
            return False, f"Status {response.status_code}: {response.text[:200]}"
    except requests.exceptions.ConnectionError as e:
        return False, f"Connection error: {e}"
    except requests.exceptions.Timeout:
        return False, "Request timed out"
    except requests.exceptions.RequestException as e:
        return False, f"Request error: {e}"


def get_json(
    session: requests.Session,
    url: str,
    headers: dict[str, str] | None = None,
    timeout: int = 30,
) -> dict[str, Any] | list[Any] | None:
    """GET request expecting JSON response.

    Args:
        session: Requests session
        url: Request URL
        headers: Optional headers
        timeout: Request timeout in seconds

    Returns:
        Parsed JSON or None on error
    """
    try:
        response = session.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return None


def post_json(
    session: requests.Session,
    url: str,
    json_data: dict[str, Any],
    headers: dict[str, str] | None = None,
    timeout: int = 30,
) -> tuple[int, dict[str, Any] | None]:
    """POST request with JSON body.

    Args:
        session: Requests session
        url: Request URL
        json_data: JSON body
        headers: Optional headers
        timeout: Request timeout in seconds

    Returns:
        Tuple of (status_code, response_json or None)
    """
    try:
        response = session.post(url, json=json_data, headers=headers, timeout=timeout)
        try:
            return response.status_code, response.json()
        except ValueError:
            return response.status_code, None
    except requests.RequestException as e:
        return 0, {"error": str(e)}


def check_endpoint_accessible(
    session: requests.Session,
    url: str,
    timeout: int = 10,
) -> bool:
    """Check if an endpoint is accessible (any response).

    Args:
        session: Requests session
        url: Endpoint URL
        timeout: Request timeout in seconds

    Returns:
        True if endpoint responds, False otherwise
    """
    try:
        session.head(url, timeout=timeout)
        return True
    except requests.RequestException:
        return False


def wait_for_endpoint(
    session: requests.Session,
    url: str,
    timeout: int = 120,
    interval: int = 5,
    expected_status: int = 200,
) -> bool:
    """Wait for an endpoint to become available.

    Args:
        session: Requests session
        url: Endpoint URL
        timeout: Maximum wait time in seconds
        interval: Polling interval in seconds
        expected_status: Expected HTTP status code

    Returns:
        True if endpoint becomes available, False on timeout
    """
    import time

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = session.get(url, timeout=10)
            if response.status_code == expected_status:
                return True
        except requests.RequestException:
            pass
        time.sleep(interval)
    return False
