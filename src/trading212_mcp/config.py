"""Environment-driven configuration for the Trading 212 MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

_ENV_HOSTS = {
    "live": "https://live.trading212.com",
    "demo": "https://demo.trading212.com",
}

_TRUTHY = {"1", "true", "yes", "on"}


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Config:
    api_key: str
    base_url: str
    allow_writes: bool
    timeout_seconds: float

    def redacted(self) -> dict[str, object]:
        return {
            "base_url": self.base_url,
            "allow_writes": self.allow_writes,
            "timeout_seconds": self.timeout_seconds,
            "api_key": "***redacted***",
        }


def load_config(env: dict[str, str] | None = None) -> Config:
    """Build a Config from environment variables.

    `.env` (if present in CWD) is loaded once. Pass `env` to bypass `os.environ`
    in tests.
    """
    if env is None:
        load_dotenv(override=False)
        env = dict(os.environ)

    api_key = env.get("TRADING212_API_KEY", "").strip()
    if not api_key:
        raise ConfigError(
            "TRADING212_API_KEY is not set. Copy .env.example to .env and add your key, "
            "or export it in your shell. Never commit the real value."
        )

    base_url_override = env.get("TRADING212_BASE_URL", "").strip()
    if base_url_override:
        base_url = base_url_override.rstrip("/")
    else:
        env_name = env.get("TRADING212_ENV", "live").strip().lower() or "live"
        if env_name not in _ENV_HOSTS:
            raise ConfigError(
                f"TRADING212_ENV must be one of {sorted(_ENV_HOSTS)}, got {env_name!r}."
            )
        base_url = _ENV_HOSTS[env_name]

    allow_writes = env.get("TRADING212_ALLOW_WRITES", "").strip().lower() in _TRUTHY

    raw_timeout = env.get("TRADING212_TIMEOUT_SECONDS", "").strip()
    try:
        timeout_seconds = float(raw_timeout) if raw_timeout else 30.0
    except ValueError as exc:
        raise ConfigError(
            f"TRADING212_TIMEOUT_SECONDS must be a number, got {raw_timeout!r}."
        ) from exc

    return Config(
        api_key=api_key,
        base_url=base_url,
        allow_writes=allow_writes,
        timeout_seconds=timeout_seconds,
    )
