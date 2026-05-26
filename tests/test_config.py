from __future__ import annotations

import pytest

from trading212_mcp.config import ConfigError, load_config


def test_missing_api_key_raises():
    with pytest.raises(ConfigError, match="TRADING212_API_KEY"):
        load_config(env={})


def test_live_default_base_url():
    cfg = load_config(env={"TRADING212_API_KEY": "k"})
    assert cfg.base_url == "https://live.trading212.com"
    assert cfg.allow_writes is False
    assert cfg.timeout_seconds == 30.0


def test_demo_env_switches_host():
    cfg = load_config(env={"TRADING212_API_KEY": "k", "TRADING212_ENV": "demo"})
    assert cfg.base_url == "https://demo.trading212.com"


def test_base_url_override_wins():
    cfg = load_config(
        env={
            "TRADING212_API_KEY": "k",
            "TRADING212_ENV": "demo",
            "TRADING212_BASE_URL": "https://example.test/",
        }
    )
    assert cfg.base_url == "https://example.test"


def test_invalid_env_rejected():
    with pytest.raises(ConfigError, match="TRADING212_ENV"):
        load_config(env={"TRADING212_API_KEY": "k", "TRADING212_ENV": "prod"})


@pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes", "on"])
def test_allow_writes_truthy(value):
    cfg = load_config(env={"TRADING212_API_KEY": "k", "TRADING212_ALLOW_WRITES": value})
    assert cfg.allow_writes is True


@pytest.mark.parametrize("value", ["", "0", "false", "no", "off", "anything-else"])
def test_allow_writes_falsy(value):
    cfg = load_config(env={"TRADING212_API_KEY": "k", "TRADING212_ALLOW_WRITES": value})
    assert cfg.allow_writes is False


def test_timeout_parses_float():
    cfg = load_config(env={"TRADING212_API_KEY": "k", "TRADING212_TIMEOUT_SECONDS": "12.5"})
    assert cfg.timeout_seconds == 12.5


def test_timeout_invalid_rejected():
    with pytest.raises(ConfigError, match="TIMEOUT"):
        load_config(env={"TRADING212_API_KEY": "k", "TRADING212_TIMEOUT_SECONDS": "soon"})


def test_redacted_hides_key():
    cfg = load_config(env={"TRADING212_API_KEY": "super-secret"})
    redacted = cfg.redacted()
    assert "super-secret" not in str(redacted)
    assert redacted["api_key"] == "***redacted***"
