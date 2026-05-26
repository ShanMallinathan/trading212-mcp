"""Pie read + (gated) write tools."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import Trading212Client


def register(mcp: FastMCP, client: Trading212Client, allow_writes: bool) -> None:
    @mcp.tool()
    async def list_pies() -> Any:
        """List all pies in the account."""
        return await client.list_pies()

    @mcp.tool()
    async def get_pie(pie_id: int) -> Any:
        """Get a single pie with its instrument allocations and progress."""
        return await client.get_pie(pie_id)

    if not allow_writes:
        return

    @mcp.tool()
    async def create_pie(pie: dict[str, Any]) -> Any:
        """Create a pie. `pie` is the full payload accepted by POST /api/v0/equity/pies
        (name, instrumentShares, goal, etc.). WRITE — modifies the account.
        """
        return await client.create_pie(pie)

    @mcp.tool()
    async def update_pie(pie_id: int, pie: dict[str, Any]) -> Any:
        """Update a pie by ID with the full payload. WRITE — modifies the account."""
        return await client.update_pie(pie_id, pie)

    @mcp.tool()
    async def delete_pie(pie_id: int) -> Any:
        """Delete a pie by ID. WRITE — irreversible."""
        return await client.delete_pie(pie_id)

    @mcp.tool()
    async def duplicate_pie(pie_id: int, body: dict[str, Any] | None = None) -> Any:
        """Duplicate a pie. `body` may include `name` and `icon` overrides. WRITE."""
        return await client.duplicate_pie(pie_id, body)
