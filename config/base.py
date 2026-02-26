"""Base configuration shared across all environments."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    """Base application configuration."""

    app_name: str = "{{ cookiecutter.project_name }}"
    debug: bool = False
    log_level: str = "INFO"

    # Database
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

    # API
    api_title: str = "{{ cookiecutter.project_name }} API"
    api_version: str = "0.1.0"
    api_description: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def database_url(self) -> str:
        """Build the database connection URL."""
        {% if cookiecutter.db_driver == "postgresql" -%}
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        {%- else -%}
        return f"sqlite+aiosqlite:///{self.db_name}"
        {%- endif %}
