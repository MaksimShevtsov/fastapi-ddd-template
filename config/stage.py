"""Staging environment configuration."""

from __future__ import annotations

from .base import BaseConfig


class StageConfig(BaseConfig):
    """Configuration for staging environment."""

    debug: bool = False
    log_level: str = "INFO"

    # Staging database settings
    {% if cookiecutter.db_driver == "postgresql" -%}
    db_host: str = "postgres-stage"
    db_port: int = 5432
    db_name: str = "{{ cookiecutter.project_slug }}_stage"
    db_user: str = "{{ cookiecutter.project_slug }}_stage_user"
    db_password: str = "changeme"  # Override via environment variable
    {%- else -%}
    db_name: str = "{{ cookiecutter.project_slug }}_stage.db"
    {%- endif %}

    model_config = {
        "env_file": ".env.stage",
        "env_file_encoding": "utf-8",
    }
