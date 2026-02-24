"""Development environment configuration."""

from __future__ import annotations

from .base import BaseConfig


class DevConfig(BaseConfig):
    """Configuration for development environment."""

    debug: bool = True
    log_level: str = "DEBUG"

    # Development database settings
    {% if cookiecutter.db_driver == "postgresql" -%}
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "{{ cookiecutter.project_slug }}_dev"
    db_user: str = "postgres"
    db_password: str = "postgres"
    {%- else -%}
    db_name: str = "{{ cookiecutter.project_slug }}_dev.db"
    {%- endif %}

    model_config = {
        "env_file": ".env.dev",
        "env_file_encoding": "utf-8",
    }
