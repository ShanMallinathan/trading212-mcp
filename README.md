# trading212-mcp

An [MCP](https://modelcontextprotocol.io) server that exposes the
[Trading 212 public API](https://t212public-api-docs.redoc.ly/) as tools an
LLM client (Claude Desktop, Claude Code, any MCP-compatible client) can call.

- Read-only by default. Order/Pie/export write tools are off unless you opt in.
- Targets the **live** Trading 212 environment by default — set `TRADING212_ENV=demo`
  if you want to start on the demo host. (A live API key only works against live;
  a demo key only works against demo.)
- The API key is loaded from `TRADING212_API_KEY` (env var or `.env`). The repo
  is structured so no secret ever lands in git.

## Setup

```bash
# clone, then from the repo root:
python -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env
# edit .env and paste your key from Trading 212 → Settings → API (Beta)
```

Run it:

```bash
trading212-mcp
# or
python -m trading212_mcp
```

The server speaks the MCP stdio transport and is meant to be launched by an MCP
client, not used interactively.

## Configuration

| Var                          | Default                         | Notes                                                                  |
| ---------------------------- | ------------------------------- | ---------------------------------------------------------------------- |
| `TRADING212_API_KEY`         | **required**                    | Trading 212 API key. Never commit.                                     |
| `TRADING212_ENV`             | `live`                          | `live` or `demo`. Selects the base URL.                                |
| `TRADING212_BASE_URL`        | (derived from `TRADING212_ENV`) | Full override, wins over `TRADING212_ENV`.                             |
| `TRADING212_ALLOW_WRITES`    | unset (off)                     | Set to `1`/`true` to register write tools.                             |
| `TRADING212_TIMEOUT_SECONDS` | `30`                            | HTTP request timeout.                                                  |

## Tools

Always available (read-only):

- `get_account_cash`, `get_account_info`
- `get_portfolio`, `get_position`
- `list_exchanges`, `list_instruments` (supports `search` and `limit`)
- `list_open_orders`, `get_order`
- `list_pies`, `get_pie`
- `list_historical_orders`, `list_dividends`, `list_transactions`, `list_exports`

Registered only when `TRADING212_ALLOW_WRITES=1`:

- `place_limit_order`, `place_market_order`, `place_stop_order`, `place_stop_limit_order`, `cancel_order`
- `create_pie`, `update_pie`, `delete_pie`, `duplicate_pie`
- `request_export`

## Wiring into Claude Desktop

`claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "trading212": {
      "command": "trading212-mcp",
      "env": {
        "TRADING212_API_KEY": "paste-your-key-here",
        "TRADING212_ENV": "demo"
      }
    }
  }
}
```

Use absolute paths or your venv's `trading212-mcp` binary if it isn't on `PATH`.

## Development

```bash
pip install -e ".[dev]"
pytest
```

Tests use `httpx.MockTransport` and never hit the real API.

## Safety notes for a public repo

- `.env` is gitignored. Only `.env.example` (placeholder values) is committed.
- The HTTP client never logs the API key, and its `repr()` redacts it.
- Write tools are off by default. Even with writes enabled, place small orders
  on `demo` first.
- Trading 212's API has per-endpoint rate limits. The client surfaces 429s with
  the `Retry-After` value so callers can back off.
