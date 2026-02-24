# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI DDD (Domain-Driven Design) template repository. Currently a skeleton — no application code exists yet. Features are built through the Speckit AI-assisted workflow.

## Intended Stack

- **Language**: Python
- **Framework**: FastAPI
- **Testing**: pytest
- **Linting/Formatting**: ruff
- **Package manager**: UV (or similar — not yet configured)

## Build/Test/Lint Commands

No `pyproject.toml` or build configuration exists yet. Once created, the intended commands are:

```bash
cd src && pytest          # run tests
ruff check .              # lint
ruff format .             # format
```

## Speckit Development Workflow

Features are built via slash commands in this order:

1. `/speckit.constitution` — set project principles (stored in `.specify/memory/constitution.md`)
2. `/speckit.specify` — create feature spec + git branch
3. `/speckit.clarify` — resolve spec ambiguities (max 5 questions)
4. `/speckit.plan` — generate implementation plan
5. `/speckit.checklist` — generate quality checklists
6. `/speckit.analyze` — read-only cross-artifact consistency check
7. `/speckit.tasks` — generate executable task list
8. `/speckit.implement` — execute tasks phase-by-phase
9. `/speckit.taskstoissues` — convert tasks to GitHub Issues

## Planned Architecture (DDD Layers)

```
src/
├── models/       # Domain models / entities
├── services/     # Business logic / use cases
├── api/          # FastAPI routes / controllers
└── lib/          # Shared utilities

tests/
├── unit/
├── integration/
└── contract/
```

## Conventions

- **Feature branches**: `NNN-short-name` (e.g., `001-user-auth`, `042-payment-flow`)
- **Feature specs**: All documentation under `specs/NNN-feature-name/` (spec.md, plan.md, tasks.md, etc.)
- **Speckit templates**: Located in `.specify/templates/`
- **Constitution**: Project principles in `.specify/memory/constitution.md` — all PRs must comply

## Active Technologies
- Python 3.11+ + FastAPI, fastapi-request-pipeline, RowQuery, Pydantic (schemas/config only), uvicorn (001-ddd-cqrs-cookiecutter)
- PostgreSQL (default), SQLite (local dev) (001-ddd-cqrs-cookiecutter)

## Recent Changes
- 001-ddd-cqrs-cookiecutter: Added Python 3.11+ + FastAPI, fastapi-request-pipeline, RowQuery, Pydantic (schemas/config only), uvicorn
