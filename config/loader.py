"""Configuration loader for environment-based settings."""

from __future__ import annotations

import os

from .base import BaseConfig
from .dev import DevConfig
from .local import LocalConfig
from .prod import ProdConfig
from .stage import StageConfig


def get_config() -> BaseConfig:
    """Load and return configuration based on APP_ENV environment variable.

    Environment values:
    - local: SQLite-based local development
    - dev: PostgreSQL development environment
    - stage: Staging environment
    - prod: Production environment (default)

    Returns:
        BaseConfig: The appropriate configuration instance for the current environment.
    """
    env = os.getenv("APP_ENV", "prod").lower()

    config_map = {
        "local": LocalConfig,
        "dev": DevConfig,
        "stage": StageConfig,
        "prod": ProdConfig,
    }

    config_class = config_map.get(env, ProdConfig)
    return config_class()  # type: ignore
