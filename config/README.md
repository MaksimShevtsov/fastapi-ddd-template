# Configuration Management

This directory contains environment-specific configurations for the application.

## Overview

Configuration is managed through Python classes that inherit from `BaseConfig`. Each environment has its own configuration module:

- **local** (`local.py`): Local development with SQLite database
- **dev** (`dev.py`): Development environment with PostgreSQL
- **stage** (`stage.py`): Staging environment (production-like)
- **prod** (`prod.py`): Production environment

## Usage

### Loading Configuration

The configuration is loaded automatically based on the `APP_ENV` environment variable:

```python
from config.loader import get_config

config = get_config()
# Or use directly from app/infrastructure/config.py
from app.infrastructure.config import config
```

### Setting the Environment

Set the `APP_ENV` variable to control which configuration is loaded:

```bash
# Local development (SQLite)
export APP_ENV=local

# Development (PostgreSQL)
export APP_ENV=dev

# Staging
export APP_ENV=stage

# Production (default)
export APP_ENV=prod
```

### Environment Files

Each environment has a corresponding `.env.*` file:

- `.env.local`: Local development settings
- `.env.dev`: Development settings
- `.env.stage`: Staging settings
- `.env.prod`: Production settings

These files are automatically loaded by Pydantic Settings based on the active configuration class.

## Configuration Hierarchy

```
BaseConfig (base.py)
├── LocalConfig (.env.local) - SQLite, debug=true
├── DevConfig (.env.dev) - PostgreSQL, debug=true
├── StageConfig (.env.stage) - PostgreSQL, debug=false
└── ProdConfig (.env.prod) - PostgreSQL, debug=false, log_level=WARNING
```

## Key Settings

### Common Across All Environments

- `app_name`: Application name
- `debug`: Debug mode (affects logging)
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `api_title`: API title
- `api_version`: API version

### Database Configuration

**Local**:
- Uses SQLite for simplicity
- File: `{project_slug}_local.db`

**Dev**:
- Uses PostgreSQL
- Database: `{project_slug}_dev`
- User: `postgres`
- Password: `postgres`

**Stage**:
- Uses PostgreSQL
- Database: `{project_slug}_stage`
- User: `{project_slug}_stage_user`
- Host: `postgres-stage`

**Prod**:
- Uses PostgreSQL
- Database: `{project_slug}`
- User: `{project_slug}_prod_user`
- Host: `postgres-prod`

## Adding New Configuration Options

1. Add the property to `BaseConfig` in `base.py`
2. Override in environment-specific config if needed
3. Add to `.env.*` files with example values
4. Update this README

## Security Notes

- **Never commit secrets** to `.env` files
- Use `.env.example` as a template for required variables
- In production, secrets should come from secure vaults or environment variables
- The `.env.*` files should be in `.gitignore` (except `.env.example`)
