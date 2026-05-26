"""Order read + (gated) write tools."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import Trading212Client


def register(mcp: FastMCP, client: Trading212Client, allow_writes: bool) -> None:
    @mcp.tool()
    async def list_open_orders() -> Any:
        """List all currently open equity orders."""
        return await client.list_open_orders()

    @mcp.tool()
    async def get_order(order_id: int) -> Any:
        """Get a single equity order by ID."""
        return await client.get_order(order_id)

    if not allow_writes:
        return

    @mcp.tool()
    async def place_limit_order(
        ticker: str,
        quantity: float,
        limit_price: float,
        time_validity: str = "DAY",
    ) -> Any:
        """Place a LIMIT order. `quantity` may be fractional and signed (negative = sell).

        `time_validity` is typically "DAY" or "GOOD_TILL_CANCEL".

        WRITE — this places a real order on the configured environment.
        """
        body = {
            "ticker": ticker,
            "quantity": quantity,
            "limitPrice": limit_price,
            "timeValidity": time_validity,
        }
        return await client.place_limit_order(body)

    @mcp.tool()
    async def place_market_order(ticker: str, quantity: float) -> Any:
        """Place a MARKET order. `quantity` may be fractional and signed (negative = sell).

        WRITE — this places a real order on the configured environment.
        """
        return await client.place_market_order({"ticker": ticker, "quantity": quantity})

    @mcp.tool()
    async def place_stop_order(
        ticker: str,
        quantity: float,
        stop_price: float,
        time_validity: str = "DAY",
    ) -> Any:
        """Place a STOP order. WRITE — places a real order."""
        body = {
            "ticker": ticker,
            "quantity": quantity,
            "stopPrice": stop_price,
            "timeValidity": time_validity,
        }
        return await client.place_stop_order(body)

    @mcp.tool()
    async def place_stop_limit_order(
        ticker: str,
        quantity: float,
        stop_price: float,
        limit_price: float,
        time_validity: str = "DAY",
    ) -> Any:
        """Place a STOP_LIMIT order. WRITE — places a real order."""
        body = {
            "ticker": ticker,
            "quantity": quantity,
            "stopPrice": stop_price,
            "limitPrice": limit_price,
            "timeValidity": time_validity,
        }
        return await client.place_stop_limit_order(body)

    @mcp.tool()
    async def cancel_order(order_id: int) -> Any:
        """Cancel an open order by ID. WRITE — affects live account."""
        return await client.cancel_order(order_id)
