"""Portfolio/position read tools."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import Trading212Client


def register(mcp: FastMCP, client: Trading212Client, allow_writes: bool) -> None:
    @mcp.tool()
    async def get_portfolio() -> Any:
        """List all open equity positions with quantity, average price, and current P&L."""
        return await client.get_portfolio()

    @mcp.tool()
    async def get_position(ticker: str) -> Any:
        """Get a single open position by Trading 212 ticker (e.g. 'AAPL_US_EQ')."""
        return await client.get_position(ticker)
