# FastAPI DDD + CQRS Template

A production-ready [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for building **domain-driven**, **CQRS-based** Python microservices with FastAPI.

```
cookiecutter gh:your-username/fastapi-ddd-template
```

---

## Why This Template?

Most FastAPI tutorials dump everything into a single file. Real services need **boundaries**. This template gives you a battle-tested 4-layer DDD architecture with CQRS separation, a request pipeline, and infrastructure that scales from SQLite prototypes to production PostgreSQL clusters.

**What you get out of the box:**

- **4-layer DDD architecture** -- Domain, Application, Infrastructure, Interfaces
- **CQRS with Command/Query buses** -- Clean write/read separation with decorator-based handler registration
- **Request pipeline** -- Composable middleware stages (auth, permissions, logging, validation)
- **JWT authentication** -- Access + refresh token flow, password hashing with bcrypt
- **Standardized error handling** -- Consistent error envelope across all endpoints
- **Raw SQL via RowQuery** -- No ORM overhead, full SQL control with named query files
- **Docker-ready** -- Multi-stage Dockerfile, per-environment compose files
- **Type-safe configuration** -- Pydantic Settings with environment-specific overrides

---

## Quick Start

### Generate a Project

```bash
pip install cookiecutter
cookiecutter gh:your-username/fastapi-ddd-template
```

You'll be prompted for:

| Variable | Default | Description |
|----------|---------|-------------|
| `project_name` | `My Service` | Human-readable service name |
| `project_slug` | auto | Python package name (derived from project_name) |
| `project_description` | `A DDD + CQRS FastAPI service` | Brief description |
| `author` | `Your Name` | Author name |
| `python_version` | `3.11` | Python version |
| `db_driver` | `postgresql` | Database driver (`postgresql` or `sqlite`) |
| `use_docker` | `true` | Generate Docker configuration |

### Run It

```bash
cd my_service

# With Docker
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Without Docker
uv sync            # or: pip install -e '.[dev]'
uvicorn app.main:app --reload
```

```bash
curl http://localhost:8000/health
# {"status": "healthy", "service": "My Service", "version": "0.1.0"}
```

---

## Architecture

```
                    ┌─────────────────────────────────────────────────┐
                    │                   Interfaces                    │
  HTTP Request ───> │   Routes  ·  Schemas  ·  Pipeline  ·  DI       │
                    └───────────────────┬─────────────────────────────┘
                                        │
                    ┌───────────────────▼─────────────────────────────┐
                    │                  Application                    │
                    │   Commands  ·  Queries  ·  Handlers  ·  Buses   │
                    └───────────────────┬─────────────────────────────┘
                                        │
                    ┌───────────────────▼─────────────────────────────┐
                    │                    Domain                       │
                    │   Entities  ·  Value Objects  ·  Errors         │
                    │   Interfaces (ABCs)  ·  Domain Services         │
                    └───────────────────┬─────────────────────────────┘
                                        │
                    ┌───────────────────▼─────────────────────────────┐
                    │                Infrastructure                   │
                    │   Repositories  ·  DB  ·  Config  ·  Security   │
                    └─────────────────────────────────────────────────┘
```

**The dependency rule:** each layer only depends on layers above it. Domain has zero external dependencies. Infrastructure implements domain interfaces. Application orchestrates domain logic. Interfaces handle HTTP.

> For a deep dive into each layer, see **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**.

---

## Project Structure

```
app/
├── domain/                  # Pure business logic (stdlib only)
│   ├── entities/            # Domain entities with invariant enforcement
│   │   ├── base.py          #   Entity[T] generic base class
│   │   └── user.py          #   UserEntity with validation rules
│   ├── value_objects/       # Immutable value types
│   │   ├── base.py          #   ValueObject base class
│   │   └── user_id.py       #   UserId (wraps UUID)
│   ├── interfaces/          # Abstract repository contracts (ABCs)
│   │   ├── user_repository.py
│   │   └── refresh_token_repository.py
│   ├── services/            # Domain services (stateless logic)
│   │   └── password_hasher.py
│   └── errors.py            # Domain error hierarchy
│
├── application/             # Use cases and orchestration
│   ├── commands/            # Write-side command DTOs
│   ├── queries/             # Read-side query DTOs
│   ├── handlers/            # Command & query handler implementations
│   │   ├── commands/        #   CreateUser, Login, Register, ...
│   │   └── queries/         #   GetUser, ...
│   ├── bus/                 # CommandBus and QueryBus
│   ├── dto/                 # Application-level data transfer objects
│   ├── read_models/         # Read-optimized Pydantic models
│   ├── services/            # Application services (e.g., TokenService)
│   └── unit_of_work.py      # UnitOfWork protocol
│
├── infrastructure/          # External systems and adapters
│   ├── config.py            # Pydantic Settings (env-aware)
│   ├── logging.py           # Structured JSON logging
│   ├── errors.py            # Infrastructure error types
│   ├── db/
│   │   ├── connection.py    # RowQuery AsyncEngine factory
│   │   ├── unit_of_work.py  # SqlUnitOfWork implementation
│   │   ├── repositories/    # Concrete repository implementations
│   │   └── queries/         # Named query helpers
│   ├── security/            # Bcrypt password hasher
│   └── sql/                 # Raw .sql files organized by entity
│       └── users/
│           ├── get_by_id.sql
│           ├── list_all.sql
│           └── insert.sql
│
├── interfaces/              # HTTP boundary
│   ├── api/
│   │   ├── routes/          # FastAPI routers (health, auth, users)
│   │   └── schemas/         # Pydantic request/response schemas
│   ├── pipeline/            # Request pipeline
│   │   ├── stages/          # Auth, Permission, Logging, Validation
│   │   └── flows.py         # Composable flow definitions
│   └── dependencies/        # FastAPI Depends() wiring
│       └── container.py     # DI container
│
├── main.py                  # App factory + exception handlers
│
tests/
├── unit/                    # Fast, isolated domain/application tests
├── integration/             # Database + service tests
└── contract/                # Full HTTP request-response tests
```

---

## CQRS in Practice

This template separates **commands** (writes) from **queries** (reads) with dedicated buses.

### Adding a Command (Write)

**1. Define the command** -- a frozen dataclass describing the intent:

```python
# app/application/commands/create_order.py
from dataclasses import dataclass

@dataclass(frozen=True)
class CreateOrderCommand:
    customer_id: str
    items: list[str]
    total_cents: int
```

**2. Create the domain entity** -- stdlib only, with invariant validation:

```python
# app/domain/entities/order.py
from app.domain.entities.base import Entity
from app.domain.value_objects.order_id import OrderId
from app.domain.errors import ValidationError

class OrderEntity(Entity[OrderId]):
    def __init__(self, *, id_: OrderId, customer_id: str, total_cents: int):
        super().__init__(id_=id_)
        self.customer_id = customer_id
        self.total_cents = total_cents

    @classmethod
    def create(cls, *, customer_id: str, total_cents: int) -> "OrderEntity":
        if total_cents <= 0:
            raise ValidationError(code="INVALID_TOTAL", message="Total must be positive")
        return cls(id_=OrderId.generate(), customer_id=customer_id, total_cents=total_cents)
```

**3. Register the handler** -- uses the `@command_handler` decorator:

```python
# app/application/handlers/commands/create_order_handler.py
from app.application.bus.command_bus import command_handler
from app.application.commands.create_order import CreateOrderCommand
from app.domain.entities.order import OrderEntity

@command_handler(CreateOrderCommand)
async def handle_create_order(command: CreateOrderCommand, uow) -> dict:
    order = OrderEntity.create(
        customer_id=command.customer_id,
        total_cents=command.total_cents,
    )
    async with uow:
        await uow.order_repository.save(order)
    return {"id": str(order.id_.value)}
```

**4. Wire the route** -- dispatch through the bus:

```python
# app/interfaces/api/routes/orders.py
@router.post("/orders", status_code=201)
async def create_order(
    body: CreateOrderRequest,
    ctx: RequestContext = Depends(flow_dependency(authenticated_flow)),
    bus: CommandBus = Depends(get_command_bus),
    uow: UnitOfWork = Depends(get_unit_of_work),
):
    result = await bus.dispatch(
        CreateOrderCommand(
            customer_id=ctx.state["user_id"],
            items=body.items,
            total_cents=body.total_cents,
        ),
        uow=uow,
    )
    return result
```

### Adding a Query (Read)

Queries bypass the domain layer entirely -- they read directly from the database into Pydantic read models.

```python
# 1. Query DTO
@dataclass(frozen=True)
class GetOrderQuery:
    order_id: str

# 2. Read model (Pydantic)
class OrderReadModel(BaseModel):
    id: str
    customer_id: str
    total_cents: int
    created_at: str

# 3. Handler -- reads directly via SQL
@query_handler(GetOrderQuery)
async def handle_get_order(query: GetOrderQuery, engine: AsyncEngine) -> OrderReadModel:
    row = await engine.fetch_one("orders.get_by_id", {"id": query.order_id})
    if not row:
        raise NotFoundError(code="ORDER_NOT_FOUND", message="Order not found")
    return OrderReadModel(**row)

# 4. SQL file: app/infrastructure/sql/orders/get_by_id.sql
# SELECT id, customer_id, total_cents, created_at FROM orders WHERE id = :id
```

---

## Request Pipeline

The template uses [`fastapi-request-pipeline`](https://github.com/your-username/fastapi-request-pipeline) for composable middleware. Instead of global middleware, you compose **flows** from **stages** and attach them per-route.

```python
# Pre-built flows
public_flow = Flow(LoggingStage())                              # Public endpoints
authenticated_flow = Flow(AuthenticationStage(), PermissionStage(), LoggingStage())  # Protected endpoints

# Use in routes
@router.get("/profile")
async def get_profile(ctx: RequestContext = Depends(flow_dependency(authenticated_flow))):
    user_id = ctx.state["user_id"]  # Set by AuthenticationStage
    ...
```

### Writing Custom Stages

```python
class RateLimitStage(FlowComponent):
    category = ComponentCategory.CUSTOM

    async def resolve(self, ctx: RequestContext) -> None:
        client_ip = ctx.request.client.host
        if await is_rate_limited(client_ip):
            ctx.abort("Rate limit exceeded")

# Compose into a new flow
rate_limited_flow = Flow(RateLimitStage(), AuthenticationStage(), LoggingStage())
```

---

## Error Handling

Every error response follows a single envelope format:

```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "User not found",
    "details": {}
  }
}
```

The domain error hierarchy maps directly to HTTP status codes:

| Error Class | Status | When to Use |
|---|---|---|
| `DomainError` | 400 | Generic domain rule violation |
| `AuthenticationError` | 401 | Invalid credentials or token |
| `AuthorizationError` | 403 | Insufficient permissions |
| `NotFoundError` | 404 | Entity does not exist |
| `ConflictError` | 409 | Duplicate resource or state conflict |
| `ValidationError` | 422 | Business rule / invariant violation |
| `RateLimitError` | 429 | Too many requests |

Infrastructure and unhandled errors always return `500` with no internal details leaked.

---

## Scaling Guide

This architecture is designed to grow with your service. See **[docs/SCALING.md](docs/SCALING.md)** for the full guide. Here's the summary:

### Stage 1: Single Service
Start here. One process, one database, SQLite or PostgreSQL. The template gives you this.

### Stage 2: Horizontal Scaling
Add workers behind a load balancer. The stateless design (JWT, no sessions) means any instance can handle any request.

### Stage 3: Read/Write Separation
CQRS makes this natural. Point `QueryBus` handlers at read replicas while `CommandBus` handlers write to the primary.

### Stage 4: Service Decomposition
Extract bounded contexts into their own services. Each domain module (entities + handlers + repository) can become its own microservice with its own database.

### Stage 5: Event-Driven
Add domain events to the bus. Publish events to a message broker (Redis Streams, RabbitMQ, Kafka). Other services subscribe and react.

---

## Configuration

Environment-aware settings via Pydantic:

```bash
# .env
APP_ENV=local
APP_NAME="My Service"
DATABASE_URL=sqlite+aiosqlite:///./dev.db
JWT_SECRET_KEY=change-me-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
LOG_LEVEL=DEBUG
```

Override per environment (`local`, `dev`, `stage`, `prod`) with environment-specific config files in `config/`.

---

## Built-In Endpoints

| Method | Path | Flow | Description |
|--------|------|------|-------------|
| `GET` | `/health` | Public | Health check |
| `POST` | `/api/v1/auth/register` | Public | Register new user |
| `POST` | `/api/v1/auth/login` | Public | Login, returns JWT tokens |
| `POST` | `/api/v1/auth/logout` | Authenticated | Invalidate refresh token |
| `POST` | `/api/v1/auth/refresh` | Public | Refresh access token |
| `POST` | `/api/v1/auth/change-password` | Authenticated | Change password |
| `GET` | `/api/v1/users/{id}` | Authenticated | Get user by ID |
| `POST` | `/api/v1/users` | Authenticated | Create user |

---

## Development

```bash
ruff check .    # Lint
ruff format .   # Format
pytest          # Run tests
```

### Test Organization

- **Unit tests** (`tests/unit/`) -- Domain entities, value objects, handlers. Fast, no I/O.
- **Integration tests** (`tests/integration/`) -- Database repositories, full handler flows.
- **Contract tests** (`tests/contract/`) -- Full HTTP request-response against the running app.

---

## Stack

| Concern | Library |
|---------|---------|
| Web framework | [FastAPI](https://fastapi.tiangolo.com/) |
| ASGI server | [Uvicorn](https://www.uvicorn.org/) |
| Request pipeline | [fastapi-request-pipeline](https://github.com/your-username/fastapi-request-pipeline) |
| Database | [RowQuery](https://github.com/your-username/row-query) (async, raw SQL) |
| Config | [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) |
| Auth | [PyJWT](https://pyjwt.readthedocs.io/) + [bcrypt](https://github.com/pyca/bcrypt) |
| Lint/Format | [Ruff](https://docs.astral.sh/ruff/) |
| Tests | [pytest](https://docs.pytest.org/) |
| Containers | Docker + docker-compose |

---

## License

MIT
