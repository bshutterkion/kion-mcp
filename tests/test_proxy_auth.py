"""Tests for proxy auth token verifier and request token helper."""

import pytest
from unittest.mock import patch, MagicMock
from kion_mcp.config.proxy_auth import KionProxyTokenVerifier, get_request_token


class TestKionProxyTokenVerifier:
    """Test the token verifier that trusts the Kion proxy."""

    @pytest.mark.asyncio
    async def test_verify_token_returns_access_token(self):
        verifier = KionProxyTokenVerifier()
        result = await verifier.verify_token("eyJhbGciOiJIUzM4NCJ9.test.sig")
        assert result is not None
        assert result.token == "eyJhbGciOiJIUzM4NCJ9.test.sig"
        assert result.client_id == "kion-proxy"

    @pytest.mark.asyncio
    async def test_verify_token_empty_string_returns_none(self):
        verifier = KionProxyTokenVerifier()
        result = await verifier.verify_token("")
        assert result is None

    @pytest.mark.asyncio
    async def test_verify_token_preserves_full_jwt(self):
        jwt = "eyJhbGciOiJIUzM4NCIsImtpZCI6IjQiLCJ0eXAiOiJKV1QifQ.eyJ1c2VySUQiOjF9.signature"
        verifier = KionProxyTokenVerifier()
        result = await verifier.verify_token(jwt)
        assert result.token == jwt


class TestGetRequestToken:
    """Test the per-request token extraction helper."""

    def test_returns_none_when_no_auth_context(self):
        token = get_request_token()
        assert token is None

    def test_returns_token_from_auth_context(self):
        mock_access_token = MagicMock()
        mock_access_token.token = "per-request-jwt"
        with patch("kion_mcp.config.proxy_auth.get_access_token", return_value=mock_access_token):
            token = get_request_token()
            assert token == "per-request-jwt"

    def test_returns_none_when_access_token_has_no_token(self):
        mock_access_token = MagicMock()
        mock_access_token.token = None
        with patch("kion_mcp.config.proxy_auth.get_access_token", return_value=mock_access_token):
            token = get_request_token()
            assert token is None
