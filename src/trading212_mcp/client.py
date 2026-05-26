"""Async HTTP client for the Trading 212 public API."""

from __future__ import annotations

from typing import Any

import httpx

from .config import Config

_API_PREFIX = "/api/v0"


class Trading212Error(RuntimeError):
    """Base class for Trading 212 API errors."""

    def __init__(self, message: str, *, status_code: int | None = None, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class AuthError(Trading212Error):
    """401/403 from Trading 212."""


class RateLimitError(Trading212Error):
    """429 from Trading 212. `retry_after` holds the server hint if present."""

    def __init__(self, message: str, *, retry_after: float | None = None, payload: Any = None):
        super().__init__(message, status_code=429, payload=payload)
        self.retry_after = retry_after


class Trading212Client:
    """Thin async wrapper. Each method maps to one T212 endpoint and returns parsed JSON."""

    def __init__(self, config: Config, transport: httpx.AsyncBaseTransport | None = None):
        self._config = config
        self._client = httpx.AsyncClient(
            base_url=config.base_url,
            headers={"Authorization": config.api_key},
            timeout=config.timeout_seconds,
            transport=transport,
        )

    def __repr__(self) -> str:
        return f"Trading212Client(base_url={self._config.base_url!r}, api_key=***redacted***)"

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "Trading212Client":
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    # ---- low-level request helper -----------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
    ) -> Any:
        url = f"{_API_PREFIX}{path}"
        try:
            response = await self._client.request(method, url, params=params, json=json)
        except httpx.HTTPError as exc:
            raise Trading212Error(f"network error calling {method} {url}: {exc}") from exc

        if response.status_code == 401 or response.status_code == 403:
            raise AuthError(
                "Trading 212 rejected the API key. Check TRADING212_API_KEY and that the key "
                "matches TRADING212_ENV (live keys only work on live, demo on demo).",
                status_code=response.status_code,
                payload=_safe_json(response),
            )
        if response.status_code == 429:
            retry_after_raw = response.headers.get("Retry-After")
            retry_after: float | None = None
            if retry_after_raw:
                try:
                    retry_after = float(retry_after_raw)
                except ValueError:
                    retry_after = None
            raise RateLimitError(
                "Trading 212 rate limit hit.",
                retry_after=retry_after,
                payload=_safe_json(response),
            )
        if response.status_code >= 400:
            raise Trading212Error(
                f"Trading 212 returned {response.status_code} for {method} {path}: "
                f"{_truncate(response.text)}",
                status_code=response.status_code,
                payload=_safe_json(response),
            )

        if not response.content:
            return None
        try:
            return response.json()
        except ValueError:
            return response.text

    # ---- account ----------------------------------------------------------

    async def get_account_cash(self) -> Any:
        return await self._request("GET", "/equity/account/cash")

    async def get_account_info(self) -> Any:
        return await self._request("GET", "/equity/account/info")

    # ---- portfolio --------------------------------------------------------

    async def get_portfolio(self) -> Any:
        return await self._request("GET", "/equity/portfolio")

    async def get_position(self, ticker: str) -> Any:
        return await self._request("GET", f"/equity/portfolio/{ticker}")

    # ---- instruments metadata --------------------------------------------

    async def list_exchanges(self) -> Any:
        return await self._request("GET", "/equity/metadata/exchanges")

    async def list_instruments(self) -> Any:
        return await self._request("GET", "/equity/metadata/instruments")

    # ---- orders -----------------------------------------------------------

    async def list_open_orders(self) -> Any:
        return await self._request("GET", "/equity/orders")

    async def get_order(self, order_id: int | str) -> Any:
        return await self._request("GET", f"/equity/orders/{order_id}")

    async def cancel_order(self, order_id: int | str) -> Any:
        return await self._request("DELETE", f"/equity/orders/{order_id}")

    async def place_limit_order(self, body: dict[str, Any]) -> Any:
        return await self._request("POST", "/equity/orders/limit", json=body)

    async def place_market_order(self, body: dict[str, Any]) -> Any:
        return await self._request("POST", "/equity/orders/market", json=body)

    async def place_stop_order(self, body: dict[str, Any]) -> Any:
        return await self._request("POST", "/equity/orders/stop", json=body)

    async def place_stop_limit_order(self, body: dict[str, Any]) -> Any:
        return await self._request("POST", "/equity/orders/stop_limit", json=body)

    # ---- pies -------------------------------------------------------------

    async def list_pies(self) -> Any:
        return await self._request("GET", "/equity/pies")

    async def get_pie(self, pie_id: int | str) -> Any:
        return await self._request("GET", f"/equity/pies/{pie_id}")

    async def create_pie(self, body: dict[str, Any]) -> Any:
        return await self._request("POST", "/equity/pies", json=body)

    async def update_pie(self, pie_id: int | str, body: dict[str, Any]) -> Any:
        return await self._request("POST", f"/equity/pies/{pie_id}", json=body)

    async def delete_pie(self, pie_id: int | str) -> Any:
        return await self._request("DELETE", f"/equity/pies/{pie_id}")

    async def duplicate_pie(self, pie_id: int | str, body: dict[str, Any] | None = None) -> Any:
        return await self._request("POST", f"/equity/pies/{pie_id}/duplicate", json=body or {})

    # ---- history ----------------------------------------------------------

    async def list_historical_orders(self, params: dict[str, Any] | None = None) -> Any:
        return await self._request("GET", "/equity/history/orders", params=params)

    async def list_dividends(self, params: dict[str, Any] | None = None) -> Any:
        return await self._request("GET", "/history/dividends", params=params)

    async def list_transactions(self, params: dict[str, Any] | None = None) -> Any:
        return await self._request("GET", "/history/transactions", params=params)

    async def list_exports(self) -> Any:
        return await self._request("GET", "/history/exports")

    async def request_export(self, body: dict[str, Any]) -> Any:
        return await self._request("POST", "/history/exports", json=body)


def _safe_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return None


def _truncate(text: str, limit: int = 500) -> str:
    return text if len(text) <= limit else text[:limit] + "..."
