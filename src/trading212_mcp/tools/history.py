"""Historical-data tools."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import Trading212Client


def register(mcp: FastMCP, client: Trading212Client, allow_writes: bool) -> None:
    @mcp.tool()
    async def list_historical_orders(
        cursor: int | None = None,
        limit: int = 50,
        ticker: str | None = None,
    ) -> Any:
        """List historical equity orders. `cursor` for pagination, `ticker` to filter."""
        params: dict[str, Any] = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor
        if ticker:
            params["ticker"] = ticker
        return await client.list_historical_orders(params)

    @mcp.tool()
    async def list_dividends(
        cursor: int | None = None,
        limit: int = 50,
        ticker: str | None = None,
    ) -> Any:
        """List paid dividends. `cursor` for pagination, `ticker` to filter."""
        params: dict[str, Any] = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor
        if ticker:
            params["ticker"] = ticker
        return await client.list_dividends(params)

    @mcp.tool()
    async def list_transactions(cursor: int | None = None, limit: int = 50) -> Any:
        """List cash transactions (deposits, withdrawals, fees)."""
        params: dict[str, Any] = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor
        return await client.list_transactions(params)

    @mcp.tool()
    async def list_exports() -> Any:
        """List previously-requested CSV exports and their statuses/download URLs."""
        return await client.list_exports()

    if not allow_writes:
        return

    @mcp.tool()
    async def request_export(body: dict[str, Any]) -> Any:
        """Request a new CSV export. `body` matches POST /api/v0/history/exports
        (date range, dataIncluded flags). WRITE — queues a job on the account.
        """
        return await client.request_export(body)
