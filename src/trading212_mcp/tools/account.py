"""Account-related read tools."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import Trading212Client


def register(mcp: FastMCP, client: Trading212Client, allow_writes: bool) -> None:
    @mcp.tool()
    async def get_account_cash() -> Any:
        """Get the account's cash balance: free, blocked, invested, P&L, etc."""
        return await client.get_account_cash()

    @mcp.tool()
    async def get_account_info() -> Any:
        """Get account metadata: currency code, account ID, and similar fields."""
        return await client.get_account_info()
