"""Tests for Thunder Identity Provider."""

import pytest
import requests

from utils.auth_helpers import (
    decode_jwt_unverified,
    get_oauth_token,
    get_oidc_config,
)
from utils.http_helpers import check_health, get_json


@pytest.mark.control_plane
@pytest.mark.smoke
class TestThunderOIDC:
    """Test Thunder OIDC discovery and configuration."""

    def test_oidc_discovery_endpoint(
        self,
        thunder_base_url: str,
        http_session: requests.Session,
    ):
        """Verify OIDC discovery endpoint is accessible."""
        config = get_oidc_config(thunder_base_url, http_session)

        assert config is not None, "OIDC discovery failed"
        assert "issuer" in config, "OIDC config missing issuer"
        assert "token_endpoint" in config, "OIDC config missing token_endpoint"
        assert "authorization_endpoint" in config, "OIDC config missing authorization_endpoint"
        assert "jwks_uri" in config, "OIDC config missing jwks_uri"

    def test_oidc_issuer_matches(
        self,
        thunder_base_url: str,
        http_session: requests.Session,
    ):
        """Verify OIDC issuer matches expected value."""
        config = get_oidc_config(thunder_base_url, http_session)

        # Issuer should match the Thunder base URL (possibly without port)
        issuer = config.get("issuer", "")
        assert "thunder" in issuer.lower() or thunder_base_url in issuer, (
            f"Unexpected issuer: {issuer}"
        )

    def test_jwks_endpoint_accessible(
        self,
        thunder_base_url: str,
        http_session: requests.Session,
    ):
        """Verify JWKS endpoint returns valid keys."""
        config = get_oidc_config(thunder_base_url, http_session)
        jwks_uri = config.get("jwks_uri")

        assert jwks_uri is not None, "JWKS URI not in OIDC config"

        jwks = get_json(http_session, jwks_uri)

        assert jwks is not None, "Failed to fetch JWKS"
        assert "keys" in jwks, "JWKS missing keys"
        assert len(jwks["keys"]) > 0, "JWKS has no keys"

        # Verify at least one RSA key exists
        rsa_keys = [k for k in jwks["keys"] if k.get("kty") == "RSA"]
        assert len(rsa_keys) > 0, "No RSA keys in JWKS"


@pytest.mark.control_plane
class TestThunderTokenEndpoint:
    """Test Thunder token issuance."""

    def test_client_credentials_flow(
        self,
        thunder_base_url: str,
        http_session: requests.Session,
    ):
        """Verify client credentials flow works."""
        import os

        client_id = os.environ.get("OAUTH_CLIENT_ID", "backstage")
        client_secret = os.environ.get("OAUTH_CLIENT_SECRET", "backstage-secret")

        try:
            token = get_oauth_token(
                token_url=f"{thunder_base_url}/oauth2/token",
                client_id=client_id,
                client_secret=client_secret,
                session=http_session,
            )

            assert token is not None, "No token returned"
            assert len(token) > 0, "Empty token returned"
        except ValueError as e:
            pytest.fail(f"Token request failed: {e}")

    def test_token_is_valid_jwt(
        self,
        thunder_base_url: str,
        http_session: requests.Session,
    ):
        """Verify issued token is a valid JWT."""
        import os

        client_id = os.environ.get("OAUTH_CLIENT_ID", "backstage")
        client_secret = os.environ.get("OAUTH_CLIENT_SECRET", "backstage-secret")

        try:
            token = get_oauth_token(
                token_url=f"{thunder_base_url}/oauth2/token",
                client_id=client_id,
                client_secret=client_secret,
                session=http_session,
            )

            # Decode without verification to check structure
            payload = decode_jwt_unverified(token)

            assert payload is not None, "Failed to decode JWT"
            assert "exp" in payload, "JWT missing expiration"
            assert "iat" in payload, "JWT missing issued-at"
        except ValueError as e:
            pytest.fail(f"Token validation failed: {e}")

    def test_token_has_expected_claims(
        self,
        thunder_base_url: str,
        http_session: requests.Session,
    ):
        """Verify token contains expected claims."""
        import os

        client_id = os.environ.get("OAUTH_CLIENT_ID", "backstage")
        client_secret = os.environ.get("OAUTH_CLIENT_SECRET", "backstage-secret")

        try:
            token = get_oauth_token(
                token_url=f"{thunder_base_url}/oauth2/token",
                client_id=client_id,
                client_secret=client_secret,
                session=http_session,
            )

            payload = decode_jwt_unverified(token)

            # Check for standard claims
            assert "iss" in payload, "JWT missing issuer claim"
            assert "sub" in payload or "client_id" in payload, (
                "JWT missing subject or client_id claim"
            )
        except ValueError as e:
            pytest.fail(f"Token claim validation failed: {e}")


@pytest.mark.control_plane
class TestThunderHealth:
    """Test Thunder service health."""

    def test_thunder_health_endpoint(
        self,
        thunder_base_url: str,
        http_session: requests.Session,
    ):
        """Verify Thunder health endpoint responds."""
        # Try common health endpoint paths
        health_paths = ["/health", "/healthz", "/.well-known/health"]

        for path in health_paths:
            is_healthy, message = check_health(http_session, f"{thunder_base_url}{path}")
            if is_healthy:
                return

        # If no health endpoint, verify OIDC discovery works as health check
        try:
            config = get_oidc_config(thunder_base_url, http_session)
            assert config is not None, "Thunder not responding"
        except Exception as e:
            pytest.fail(f"Thunder health check failed: {e}")
