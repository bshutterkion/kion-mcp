"""Tests for per-request token handling in make_authenticated_request."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from kion_mcp.utils.http_helper import make_authenticated_request, build_standard_headers


class TestPerRequestToken:
    """Test that make_authenticated_request uses per-request token when available."""

    @pytest.mark.asyncio
    async def test_uses_per_request_token_when_available(self, oauth_config):
        """When a per-request token exists (HTTP mode), use it instead of client headers."""
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)

        mock_auth_manager = MagicMock()

        with patch("kion_mcp.utils.http_helper.get_request_token", return_value="per-request-user-jwt"):
            response = await make_authenticated_request(
                mock_client, "GET", "/v3/app-config",
                oauth_config, mock_auth_manager, None
            )
            # Verify the request was made with per-request token headers
            call_kwargs = mock_client.request.call_args
            assert call_kwargs.kwargs.get("headers") is not None
            assert "per-request-user-jwt" in call_kwargs.kwargs["headers"]["Authorization"]

    @pytest.mark.asyncio
    async def test_falls_back_to_client_headers_when_no_request_token(self, oauth_config):
        """When no per-request token (stdio mode), use the client's default headers."""
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)

        mock_auth_manager = MagicMock()

        with patch("kion_mcp.utils.http_helper.get_request_token", return_value=None):
            response = await make_authenticated_request(
                mock_client, "GET", "/v3/app-config",
                oauth_config, mock_auth_manager, None
            )
            # Verify the request was made WITHOUT explicit headers (uses client defaults)
            call_kwargs = mock_client.request.call_args
            assert call_kwargs.kwargs.get("headers") is None
