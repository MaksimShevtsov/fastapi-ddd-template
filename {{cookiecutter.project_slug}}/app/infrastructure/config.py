"""Centralized application configuration using Pydantic Settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    app_name: str = "{{ cookiecutter.project_name }}"
    debug: bool = False
    log_level: str = "INFO"

    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    admin_enabled: bool = False
    admin_session_secret: str = "change-me-in-production"
    admin_https_only: bool = False

    db_driver: str = "{{ cookiecutter.db_driver }}"
    {% if cookiecutter.db_driver == "postgresql" -%}
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "{{ cookiecutter.project_slug }}"
    db_user: str = "postgres"
    db_password: str = "postgres"
    {%- else -%}
    db_host: str = ""
    db_port: int = 0
    db_name: str = "{{ cookiecutter.project_slug }}.db"
    db_user: str = ""
    db_password: str = ""
    {%- endif %}

    @property
    def database_url(self) -> str:
        """Build the database connection URL."""
        {% if cookiecutter.db_driver == "postgresql" -%}
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        {%- else -%}
        return f"sqlite+aiosqlite:///{self.db_name}"
        {%- endif %}

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}
