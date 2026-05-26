from __future__ import annotations

import json

import httpx
import pytest

from trading212_mcp.client import AuthError, RateLimitError, Trading212Client, Trading212Error
from trading212_mcp.config import Config


def _config(base_url: str = "https://live.trading212.com") -> Config:
    return Config(api_key="test-key", base_url=base_url, allow_writes=False, timeout_seconds=5.0)


def _make_client(handler) -> Trading212Client:
    return Trading212Client(_config(), transport=httpx.MockTransport(handler))


async def test_sends_auth_header_and_returns_json():
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["auth"] = request.headers.get("authorization")
        seen["url"] = str(request.url)
        return httpx.Response(200, json={"free": 100.0})

    client = _make_client(handler)
    try:
        result = await client.get_account_cash()
    finally:
        await client.aclose()

    assert result == {"free": 100.0}
    assert seen["auth"] == "test-key"
    assert seen["url"].endswith("/api/v0/equity/account/cash")


async def test_401_maps_to_auth_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"code": "BadRequest"})

    client = _make_client(handler)
    try:
        with pytest.raises(AuthError) as info:
            await client.get_account_info()
    finally:
        await client.aclose()
    assert info.value.status_code == 401


async def test_429_maps_to_rate_limit_with_retry_after():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, headers={"Retry-After": "2.5"}, json={"code": "Throttled"})

    client = _make_client(handler)
    try:
        with pytest.raises(RateLimitError) as info:
            await client.get_portfolio()
    finally:
        await client.aclose()
    assert info.value.retry_after == 2.5


async def test_generic_4xx_raises_trading212_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"code": "BadRequest"})

    client = _make_client(handler)
    try:
        with pytest.raises(Trading212Error) as info:
            await client.get_portfolio()
    finally:
        await client.aclose()
    assert info.value.status_code == 400


async def test_post_sends_json_body():
    seen: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["method"] = request.method
        seen["path"] = request.url.path
        seen["body"] = json.loads(request.content.decode() or "null")
        return httpx.Response(200, json={"id": 1})

    client = _make_client(handler)
    try:
        await client.place_market_order({"ticker": "AAPL_US_EQ", "quantity": 1})
    finally:
        await client.aclose()

    assert seen["method"] == "POST"
    assert seen["path"] == "/api/v0/equity/orders/market"
    assert seen["body"] == {"ticker": "AAPL_US_EQ", "quantity": 1}


def test_repr_redacts_api_key():
    client = Trading212Client(_config(), transport=httpx.MockTransport(lambda r: httpx.Response(204)))
    text = repr(client)
    assert "test-key" not in text
    assert "redacted" in text.lower()
