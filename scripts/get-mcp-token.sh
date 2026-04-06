#!/bin/bash
# Fetches an OAuth2 access token from Thunder for OpenChoreo MCP access.
# Used by MCP clients (Claude Code, pi, Cursor) as a token provider.
#
# Usage: ./scripts/get-mcp-token.sh
# Output: Bearer token on stdout

set -euo pipefail

THUNDER_URL="${THUNDER_URL:-https://thunder.openchoreo.local:8443}"
CLIENT_ID="${MCP_CLIENT_ID:-service_mcp_client}"
CLIENT_SECRET="${MCP_CLIENT_SECRET:-service_mcp_client_secret}"

TOKEN_RESPONSE=$(curl -sk --max-time 10 -X POST "${THUNDER_URL}/oauth2/token" \
  -u "${CLIENT_ID}:${CLIENT_SECRET}" \
  -d "grant_type=client_credentials" \
  -d "scope=openid" 2>/dev/null)

echo "$TOKEN_RESPONSE" | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])"
