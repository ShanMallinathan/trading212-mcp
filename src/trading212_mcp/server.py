"""FastMCP server entry point."""

from __future__ import annotations

import sys

from mcp.server.fastmcp import FastMCP

from .client import Trading212Client
from .config import Config, ConfigError, load_config
from .tools import account, history, instruments, orders, pies, portfolio

_TOOL_MODULES = (account, portfolio, instruments, orders, pies, history)


def build_server(config: Config | None = None) -> tuple[FastMCP, Trading212Client]:
    """Build a FastMCP server and its client. Useful for tests."""
    config = config or load_config()
    mcp = FastMCP("trading212")
    client = Trading212Client(config)
    for module in _TOOL_MODULES:
        module.register(mcp, client, config.allow_writes)
    return mcp, client


def main() -> None:
    try:
        config = load_config()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        sys.exit(2)

    mcp, _client = build_server(config)
    mode = "READ+WRITE" if config.allow_writes else "READ-ONLY"
    print(
        f"trading212-mcp starting | base_url={config.base_url} | mode={mode}",
        file=sys.stderr,
    )
    mcp.run()


if __name__ == "__main__":
    main()
