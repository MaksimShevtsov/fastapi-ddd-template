"""Local development configuration."""

from __future__ import annotations

from .base import BaseConfig


class LocalConfig(BaseConfig):
    """Configuration for local development environment."""

    debug: bool = True
    log_level: str = "DEBUG"

    # Use SQLite for local development
    db_driver: str = "sqlite"
    {% if cookiecutter.db_driver == "postgresql" -%}
    db_name: str = "{{ cookiecutter.project_slug }}_local.db"
    {%- else -%}
    db_name: str = "{{ cookiecutter.project_slug }}_local.db"
    {%- endif %}

    model_config = {
        "env_file": ".env.local",
        "env_file_encoding": "utf-8",
    }
