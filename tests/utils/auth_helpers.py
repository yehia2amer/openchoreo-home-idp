"""OAuth2 authentication helper functions."""

from typing import Any

import requests


def get_oauth_token(
    token_url: str,
    client_id: str,
    client_secret: str,
    session: requests.Session | None = None,
    scope: str = "openid profile email",
    grant_type: str = "client_credentials",
) -> str:
    """Get OAuth2 access token using client credentials flow.

    Args:
        token_url: Token endpoint URL
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        session: Optional requests session (creates new if None)
        scope: OAuth2 scope
        grant_type: OAuth2 grant type

    Returns:
        Access token string

    Raises:
        ValueError: If token request fails
    """
    if session is None:
        session = requests.Session()
        session.verify = False

    response = session.post(
        token_url,
        data={
            "grant_type": grant_type,
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )

    if response.status_code != 200:
        raise ValueError(
            f"Token request failed with status {response.status_code}: {response.text}"
        )

    token_data = response.json()
    access_token = token_data.get("access_token")

    if not access_token:
        raise ValueError(f"No access_token in response: {token_data}")

    return access_token


def get_oauth_token_password(
    token_url: str,
    client_id: str,
    client_secret: str,
    username: str,
    password: str,
    session: requests.Session | None = None,
    scope: str = "openid profile email",
) -> dict[str, Any]:
    """Get OAuth2 tokens using password grant flow.

    Args:
        token_url: Token endpoint URL
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        username: User's username
        password: User's password
        session: Optional requests session
        scope: OAuth2 scope

    Returns:
        Token response dict with access_token, refresh_token, etc.

    Raises:
        ValueError: If token request fails
    """
    if session is None:
        session = requests.Session()
        session.verify = False

    response = session.post(
        token_url,
        data={
            "grant_type": "password",
            "client_id": client_id,
            "client_secret": client_secret,
            "username": username,
            "password": password,
            "scope": scope,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )

    if response.status_code != 200:
        raise ValueError(
            f"Token request failed with status {response.status_code}: {response.text}"
        )

    return response.json()


def refresh_oauth_token(
    token_url: str,
    client_id: str,
    client_secret: str,
    refresh_token: str,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """Refresh OAuth2 access token.

    Args:
        token_url: Token endpoint URL
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        refresh_token: Refresh token
        session: Optional requests session

    Returns:
        Token response dict with new access_token

    Raises:
        ValueError: If refresh fails
    """
    if session is None:
        session = requests.Session()
        session.verify = False

    response = session.post(
        token_url,
        data={
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )

    if response.status_code != 200:
        raise ValueError(
            f"Token refresh failed with status {response.status_code}: {response.text}"
        )

    return response.json()


def decode_jwt_unverified(token: str) -> dict[str, Any]:
    """Decode JWT without verification (for inspection only).

    Args:
        token: JWT token string

    Returns:
        Decoded payload dict
    """
    import base64
    import json

    # Split token into parts
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid JWT format")

    # Decode payload (second part)
    payload = parts[1]
    # Add padding if needed
    padding = 4 - len(payload) % 4
    if padding != 4:
        payload += "=" * padding

    decoded = base64.urlsafe_b64decode(payload)
    return json.loads(decoded)


def verify_jwt_signature(
    token: str,
    jwks_url: str,
    session: requests.Session | None = None,
    algorithms: list[str] | None = None,
) -> dict[str, Any]:
    """Verify JWT signature against JWKS.

    Args:
        token: JWT token string
        jwks_url: JWKS endpoint URL
        session: Optional requests session
        algorithms: Allowed algorithms (default: RS256)

    Returns:
        Decoded and verified payload

    Raises:
        ValueError: If verification fails
    """
    import jwt
    from jwt import PyJWKClient

    if algorithms is None:
        algorithms = ["RS256"]

    if session is None:
        session = requests.Session()
        session.verify = False

    # Fetch JWKS
    response = session.get(jwks_url, timeout=30)
    response.raise_for_status()
    jwks = response.json()

    # Create JWKS client
    jwk_client = PyJWKClient(jwks_url)
    signing_key = jwk_client.get_signing_key_from_jwt(token)

    # Verify and decode
    return jwt.decode(
        token,
        signing_key.key,
        algorithms=algorithms,
        options={"verify_aud": False},  # Skip audience verification
    )


def get_oidc_config(
    issuer_url: str,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """Fetch OIDC discovery configuration.

    Args:
        issuer_url: OIDC issuer URL
        session: Optional requests session

    Returns:
        OIDC configuration dict

    Raises:
        ValueError: If fetch fails
    """
    if session is None:
        session = requests.Session()
        session.verify = False

    well_known_url = f"{issuer_url.rstrip('/')}/.well-known/openid-configuration"

    response = session.get(well_known_url, timeout=30)

    if response.status_code != 200:
        raise ValueError(
            f"OIDC discovery failed with status {response.status_code}: {response.text}"
        )

    return response.json()
