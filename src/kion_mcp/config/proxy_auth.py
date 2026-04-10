"""Proxy authentication for remote MCP hosting behind the Kion proxy."""

import logging
from typing import Optional

from fastmcp.server.auth.auth import AccessToken, TokenVerifier
from mcp.server.auth.middleware.auth_context import get_access_token


class KionProxyTokenVerifier(TokenVerifier):
    """Token verifier that trusts tokens pre-validated by the Kion proxy.

    When kion-mcp runs behind the Kion MCP proxy, the proxy's JWT middleware
    has already validated the Bearer token. This verifier simply passes the
    raw token through so it can be used for downstream Kion API calls.
    """

    async def verify_token(self, token: str) -> Optional[AccessToken]:
        if not token:
            return None
        return AccessToken(token=token, client_id="kion-proxy", scopes=[])


def get_request_token() -> Optional[str]:
    """Get the per-request Bearer token from the HTTP auth context.

    Returns the raw token string if running in HTTP mode behind the proxy,
    or None if no per-request token is available (stdio mode).
    """
    access_token = get_access_token()
    if access_token and access_token.token:
        return access_token.token
    return None
