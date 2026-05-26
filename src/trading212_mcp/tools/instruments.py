"""Instrument metadata tools."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import Trading212Client


def register(mcp: FastMCP, client: Trading212Client, allow_writes: bool) -> None:
    @mcp.tool()
    async def list_exchanges() -> Any:
        """List exchanges Trading 212 supports and their working schedules."""
        return await client.list_exchanges()

    @mcp.tool()
    async def list_instruments(search: str | None = None, limit: int = 50) -> Any:
        """List tradable instruments.

        The full Trading 212 instruments list is large (thousands of rows). Pass
        `search` to filter by ticker, ISIN, short-name, or full-name (case-insensitive
        substring match), and `limit` to cap the rows returned. Set `limit=0` to
        return everything (use sparingly).
        """
        instruments = await client.list_instruments()
        if not isinstance(instruments, list):
            return instruments

        if search:
            needle = search.lower()
            fields = ("ticker", "isin", "shortName", "name", "type")
            instruments = [
                item
                for item in instruments
                if any(
                    isinstance(item.get(field), str) and needle in item[field].lower()
                    for field in fields
                )
            ]

        if limit and limit > 0:
            instruments = instruments[:limit]
        return instruments
