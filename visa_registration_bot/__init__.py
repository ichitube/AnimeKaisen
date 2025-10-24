"""Standalone visa registration bot package."""

from .config import BotConfig, ConfigError, load_config

__all__ = ["BotConfig", "ConfigError", "load_config"]
