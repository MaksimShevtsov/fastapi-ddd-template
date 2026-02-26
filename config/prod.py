"""Production environment configuration."""

from __future__ import annotations

from .base import BaseConfig


class ProdConfig(BaseConfig):
    """Configuration for production environment."""

    debug: bool = False
    log_level: str = "WARNING"

    # Production database settings (must be provided via environment variables)
    {% if cookiecutter.db_driver == "postgresql" -%}
    db_host: str = "postgres-prod"
    db_port: int = 5432
    db_name: str = "{{ cookiecutter.project_slug }}"
    db_user: str = "{{ cookiecutter.project_slug }}_prod_user"
    db_password: str  # Required environment variable
    {%- else -%}
    db_name: str = "{{ cookiecutter.project_slug }}.db"
    {%- endif %}

    model_config = {
        "env_file": ".env.prod",
        "env_file_encoding": "utf-8",
    }
