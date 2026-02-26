# Architecture Guide

This document explains each layer of the DDD + CQRS architecture, why it exists, and how the layers interact.

---

## Table of Contents

- [The Big Picture](#the-big-picture)
- [Layer 1: Domain](#layer-1-domain)
- [Layer 2: Application](#layer-2-application)
- [Layer 3: Infrastructure](#layer-3-infrastructure)
- [Layer 4: Interfaces](#layer-4-interfaces)
- [How a Request Flows Through the System](#how-a-request-flows-through-the-system)
- [The Dependency Rule](#the-dependency-rule)
- [CQRS: Why Separate Reads and Writes?](#cqrs-why-separate-reads-and-writes)
- [Key Design Decisions](#key-design-decisions)

---

## The Big Picture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  Client (browser, mobile app, another service)                         │
│                                                                         │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │ HTTP
┌──────────────────────────────▼──────────────────────────────────────────┐
│  INTERFACES                                                             │
│                                                                         │
│  ┌──────────┐  ┌────────────────┐  ┌──────────┐  ┌───────────────┐     │
│  │  Routes   │  │  Pipeline      │  │  Schemas │  │  Dependencies │     │
│  │  (FastAPI │  │  (Auth, Perms, │  │ (Pydantic│  │  (DI wiring)  │     │
│  │  routers) │  │   Logging)     │  │  models) │  │               │     │
│  └─────┬─────┘  └───────┬────────┘  └──────────┘  └───────────────┘     │
│        │                │                                               │
│        └────────┬───────┘                                               │
│                 │ dispatches commands/queries                            │
└─────────────────┼───────────────────────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────────────────────┐
│  APPLICATION                                                            │
│                                                                         │
│  ┌────────────┐  ┌───────────┐  ┌──────────────────┐  ┌─────────┐      │
│  │  Commands   │  │  Queries  │  │  Handlers         │  │  Buses  │      │
│  │  (frozen    │  │  (frozen  │  │  (async functions  │  │ Command │      │
│  │  dataclass) │  │  dataclass│  │  w/ @decorator)    │  │  Query  │      │
│  └─────────────┘  └──────────┘  └────────┬───────────┘  └─────────┘      │
│                                          │                              │
│       ┌──────────┐  ┌──────────────┐     │   ┌──────────────┐           │
│       │   DTOs   │  │  Read Models │     │   │ Unit of Work │           │
│       └──────────┘  └──────────────┘     │   │  (protocol)  │           │
│                                          │   └──────────────┘           │
└──────────────────────────────────────────┼──────────────────────────────┘
                                           │
┌──────────────────────────────────────────▼──────────────────────────────┐
│  DOMAIN                                                                 │
│                                                                         │
│  ┌────────────┐  ┌───────────────┐  ┌────────────┐  ┌───────────────┐   │
│  │  Entities   │  │ Value Objects │  │  Errors    │  │  Interfaces   │   │
│  │  (User,     │  │ (UserId,     │  │  hierarchy │  │  (Repository  │   │
│  │   Order...) │  │  Email...)    │  │            │  │   ABCs)       │   │
│  └─────────────┘  └───────────────┘  └────────────┘  └───────────────┘   │
│                                                                         │
│  ┌──────────────────┐                                                   │
│  │  Domain Services  │   *** stdlib only — zero external deps ***       │
│  └──────────────────┘                                                   │
│                                                                         │
└──────────────────────────────────────────┬──────────────────────────────┘
                                           │ implements interfaces
┌──────────────────────────────────────────▼──────────────────────────────┐
│  INFRASTRUCTURE                                                         │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────┐  ┌──────────────────┐  │
│  │ Repositories  │  │  Database    │  │  Config │  │  Security        │  │
│  │ (concrete     │  │  (RowQuery   │  │ (Pydantic│  │  (bcrypt,       │  │
│  │  impls of     │  │   engine,    │  │ Settings)│  │   JWT helpers)  │  │
│  │  domain ABCs) │  │   raw SQL)   │  │         │  │                 │  │
│  └──────────────┘  └──────────────┘  └─────────┘  └──────────────────┘  │
│                                                                         │
│  ┌──────────────┐  ┌──────────────┐                                     │
│  │ Unit of Work  │  │  SQL Files   │                                     │
│  │ (transaction  │  │  (.sql per   │                                     │
│  │  management)  │  │   entity)    │                                     │
│  └──────────────┘  └──────────────┘                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Domain

**Purpose:** Encode the business rules of your application. Nothing else.

**Location:** `app/domain/`

**Rules:**
- Standard library only. No FastAPI, no Pydantic, no database imports.
- Entities enforce their own invariants via validation in factory methods.
- Value objects are immutable and compared by value, not identity.
- Repository interfaces (ABCs) define *what* persistence operations exist, not *how* they work.

### Entities

Entities have identity (an ID that persists across state changes) and enforce business invariants.

```python
class UserEntity(Entity[UserId]):
    """User domain entity with invariant enforcement."""

    @classmethod
    def create(cls, *, name: str, email: str, password_hash: str) -> UserEntity:
        """Factory method — validates invariants before creation."""
        cls._validate_name(name)      # name must be non-empty
        cls._validate_email(email)    # email must contain @
        return cls(
            id_=UserId.generate(),
            name=name,
            email=email,
            password_hash=password_hash,
            created_at=datetime.now(UTC),
        )

    @staticmethod
    def _validate_name(name: str) -> None:
        if not name or not name.strip():
            raise ValidationError(code="INVALID_NAME", message="Name must be non-empty")
```

Key points:
- **Factory methods** (`create`) are the only way to construct entities. They validate all invariants upfront.
- **Mutation methods** (`update_password`, `update_name`) re-validate invariants on every change.
- **No database knowledge.** The entity doesn't know how it's stored.

### Value Objects

Immutable, identity-less types that wrap primitive values with meaning:

```python
class UserId(ValueObject[uuid.UUID]):
    """Wraps a UUID to prevent accidentally passing raw strings as user IDs."""

    @classmethod
    def generate(cls) -> UserId:
        return cls(value=uuid.uuid4())
```

Why bother? Because `user_id: str` tells you nothing, but `user_id: UserId` tells you exactly what it is. The type system catches misuse at development time.

### Domain Errors

A hierarchy of errors that map to business outcomes:

```
DomainError (400)
├── NotFoundError (404)        # Entity doesn't exist
├── ConflictError (409)        # Duplicate / state conflict
├── ValidationError (422)      # Business rule violated
├── AuthenticationError (401)  # Bad credentials
├── AuthorizationError (403)   # Insufficient permissions
└── RateLimitError (429)       # Too many requests
```

Each error carries a machine-readable `code`, human-readable `message`, and optional `details` dict. The interfaces layer maps these to HTTP status codes automatically.

### Repository Interfaces

Abstract contracts that define persistence operations without implementation:

```python
class UserRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> UserEntity | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> UserEntity | None: ...

    @abstractmethod
    async def save(self, user: UserEntity) -> None: ...
```

This is the **Dependency Inversion Principle** in action. The domain defines what it needs; infrastructure provides it.

---

## Layer 2: Application

**Purpose:** Orchestrate domain logic into use cases. No business rules here -- just coordination.

**Location:** `app/application/`

### Commands and Queries

Commands represent **intent to change state**. Queries represent **intent to read state**. Both are frozen dataclasses -- immutable data bags with no behavior.

```python
# Command (write)
@dataclass(frozen=True)
class CreateUserCommand:
    name: str
    email: str
    password: str

# Query (read)
@dataclass(frozen=True)
class GetUserQuery:
    user_id: str
```

### Handlers

Handlers implement use cases. Each handler does one thing:

```python
@command_handler(CreateUserCommand)
async def handle_create_user(command: CreateUserCommand, uow, hasher) -> UserDTO:
    # 1. Use domain service to hash password
    password_hash = hasher.hash(command.password)

    # 2. Create entity (domain validates invariants)
    user = UserEntity.create(name=command.name, email=command.email, password_hash=password_hash)

    # 3. Persist via unit of work
    async with uow:
        await uow.user_repository.save(user)

    # 4. Return application-level DTO (not the entity)
    return UserDTO(id=str(user.id_.value), name=user.name, email=user.email)
```

The `@command_handler(CommandType)` decorator registers the function in the `CommandBus`. No manual wiring needed.

### Command Bus and Query Bus

The buses are registries that dispatch commands/queries to their handlers:

```python
class CommandBus:
    _handlers: dict[type, Callable] = {}

    @classmethod
    def handler(cls, command_type: type) -> Callable:
        """Decorator to register a command handler."""
        def decorator(func):
            cls._handlers[command_type] = func
            return func
        return decorator

    async def dispatch(self, command, **kwargs):
        handler = self._handlers[type(command)]
        return await handler(command, **kwargs)
```

Routes dispatch through the bus, never calling handlers directly. This gives you a single point to add cross-cutting concerns (logging, metrics, retries) later.

### Unit of Work

The `UnitOfWork` protocol defines transactional boundaries:

```python
async with uow:
    await uow.user_repository.save(user)
    await uow.order_repository.save(order)
    # Both succeed or both roll back
```

---

## Layer 3: Infrastructure

**Purpose:** Connect the application to the outside world -- databases, external APIs, file systems.

**Location:** `app/infrastructure/`

### Database (RowQuery)

This template uses **raw SQL** via RowQuery instead of an ORM. SQL files are organized per entity:

```
app/infrastructure/sql/
└── users/
    ├── get_by_id.sql      # SELECT * FROM users WHERE id = :id
    ├── get_by_email.sql   # SELECT * FROM users WHERE email = :email
    ├── list_all.sql       # SELECT * FROM users ORDER BY created_at DESC
    └── insert.sql         # INSERT INTO users (id, name, email, ...) VALUES (...)
```

The `AsyncEngine` factory creates the connection:

```python
def create_engine(settings: Settings) -> AsyncEngine:
    config = ConnectionConfig(url=settings.database_url)
    registry = SQLRegistry(directory="app/infrastructure/sql")
    return AsyncEngine(config=config, registry=registry)
```

Why raw SQL?
- Full control over query performance
- No N+1 surprises
- Easy to optimize with `EXPLAIN ANALYZE`
- Database-specific features (window functions, CTEs, etc.) are always available

### Repositories

Concrete implementations of domain repository interfaces:

```python
class UserRepository(UserRepositoryInterface):
    """Implements user persistence with RowQuery."""

    def __init__(self, transaction):
        self._tx = transaction

    async def get_by_id(self, user_id: UserId) -> UserEntity | None:
        row = await self._tx.fetch_one("users.get_by_id", {"id": str(user_id.value)})
        return self._to_entity(row) if row else None

    async def save(self, user: UserEntity) -> None:
        await self._tx.execute("users.insert", {
            "id": str(user.id_.value),
            "name": user.name,
            "email": user.email,
            "password_hash": user.password_hash,
            "created_at": user.created_at.isoformat(),
        })
```

### SqlUnitOfWork

Wraps a database transaction and provides repository access:

```python
class SqlUnitOfWork:
    async def __aenter__(self):
        self._transaction = await self._engine.transaction().__aenter__()
        self._user_repository = UserRepository(self._transaction)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._transaction.__aexit__(exc_type, exc_val, exc_tb)
```

### Configuration

Pydantic Settings with environment variable support:

```python
class Settings(BaseSettings):
    app_name: str = "My Service"
    app_env: str = "local"
    database_url: str = "sqlite+aiosqlite:///./dev.db"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env")
```

---

## Layer 4: Interfaces

**Purpose:** Translate HTTP into application commands/queries and translate results back to HTTP.

**Location:** `app/interfaces/`

### Routes

Thin FastAPI routers. Their only job is:
1. Parse the HTTP request (via Pydantic schemas)
2. Run the pipeline flow (auth, permissions, etc.)
3. Dispatch a command or query
4. Return the result

```python
@router.post("/users", status_code=201)
async def create_user(
    body: CreateUserRequest,
    ctx: RequestContext = Depends(flow_dependency(authenticated_flow)),
    bus: CommandBus = Depends(get_command_bus),
    uow = Depends(get_unit_of_work),
    hasher = Depends(get_password_hasher),
):
    return await bus.dispatch(
        CreateUserCommand(name=body.name, email=body.email, password=body.password),
        uow=uow,
        hasher=hasher,
    )
```

Routes should contain **zero business logic**. If you find yourself writing `if/else` in a route, that logic belongs in a handler.

### Request Pipeline

Instead of global middleware that runs on every request, the pipeline lets you compose **flows** from **stages** and attach them per-route:

```python
# Stages are reusable building blocks
class AuthenticationStage(FlowComponent):
    category = ComponentCategory.AUTHENTICATION

    async def resolve(self, ctx: RequestContext) -> None:
        # Extract JWT, validate, set ctx.state["user_id"]
        ...

# Flows compose stages for specific use cases
public_flow = Flow(LoggingStage())
authenticated_flow = Flow(AuthenticationStage(), PermissionStage(), LoggingStage())

# Routes declare which flow they need
@router.get("/profile")
async def get_profile(ctx = Depends(flow_dependency(authenticated_flow))):
    ...
```

This is more flexible than middleware because:
- Different routes can have different pipeline compositions
- Stages are testable in isolation
- No "exclude this path" workarounds for middleware

### Schemas

Pydantic models for HTTP serialization. Separate from domain entities and application DTOs:

```python
class CreateUserRequest(BaseModel):
    name: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
```

### Exception Handlers

The app factory registers exception handlers that convert domain/infrastructure errors into the standardized error envelope:

```python
@app.exception_handler(DomainError)
async def domain_error_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )
```

---

## How a Request Flows Through the System

Let's trace a `POST /api/v1/users` request end-to-end:

```
1. HTTP Request arrives
   POST /api/v1/users  { "name": "Alice", "email": "alice@example.com", "password": "secret" }
       │
2. FastAPI matches route
   └─> create_user() in app/interfaces/api/routes/users.py
       │
3. Pydantic validates request body
   └─> CreateUserRequest schema validates name, email, password
       │
4. Pipeline flow executes
   └─> authenticated_flow runs:
       ├─ AuthenticationStage: validates JWT → sets ctx.state["user_id"]
       ├─ PermissionStage: checks permissions
       └─ LoggingStage: logs request metadata
       │
5. Route dispatches command through bus
   └─> bus.dispatch(CreateUserCommand(name="Alice", ...))
       │
6. CommandBus finds registered handler
   └─> handle_create_user() in app/application/handlers/commands/
       │
7. Handler orchestrates domain logic
   ├─ PasswordHasher hashes the password
   ├─ UserEntity.create() validates invariants (name non-empty, email has @)
   │   └─ If invalid: raises ValidationError → HTTP 422
   └─ UnitOfWork opens transaction
       ├─ UserRepository.save() executes INSERT SQL
       └─ Transaction commits (or rolls back on error)
       │
8. Handler returns UserDTO
   └─> {"id": "550e8400-...", "name": "Alice", "email": "alice@example.com"}
       │
9. FastAPI serializes response
   └─> HTTP 201  {"id": "550e8400-...", "name": "Alice", "email": "alice@example.com"}
```

---

## The Dependency Rule

```
  Interfaces  ──depends on──>  Application  ──depends on──>  Domain
       │                            │
       │                            │
       └───── depends on ───────────┼──────> Infrastructure
                                    │              │
                                    │              │
                                    └── implements─┘
```

- **Domain** depends on nothing. It's pure Python.
- **Application** depends on Domain (uses entities, value objects, errors, repository interfaces).
- **Infrastructure** depends on Domain (implements repository interfaces) and external libraries.
- **Interfaces** depends on Application (dispatches commands/queries) and Infrastructure (DI wiring).

**Infrastructure never imports from Application.** Application depends on domain interfaces; infrastructure implements them. This inversion is what makes the architecture testable -- you can swap PostgreSQL for an in-memory repository in tests.

---

## CQRS: Why Separate Reads and Writes?

### The Problem

In a traditional architecture, the same model handles both reads and writes. This creates tension:

- **Writes** need rich domain objects with validation and business rules.
- **Reads** need flat, fast projections optimized for display.

Trying to serve both needs with one model leads to bloated entities, lazy loading hacks, and N+1 queries.

### The Solution

| | Write Side (Commands) | Read Side (Queries) |
|---|---|---|
| **Data model** | Domain entities | Pydantic read models |
| **Validation** | Domain invariants | None (data is already valid) |
| **Persistence** | UnitOfWork + Repository | Direct SQL query |
| **Optimization** | Correctness-first | Performance-first |
| **Bus** | CommandBus | QueryBus |

Commands go through the full domain layer: create entity, validate, persist via repository.

Queries skip the domain layer entirely: execute a SQL query, map the result to a Pydantic model, return.

This means you can:
- Add read-optimized views/materialized views without touching domain code
- Point queries at read replicas without changing handlers
- Cache query results independently of write operations

---

## Key Design Decisions

### 1. Raw SQL Over ORM

**Decision:** Use RowQuery with `.sql` files instead of SQLAlchemy/Tortoise.

**Why:** ORMs add a layer of abstraction that often fights you at scale. Raw SQL gives you full control over query plans, lets you use database-specific features, and makes performance predictable.

**Trade-off:** More boilerplate for simple CRUD. Worth it when queries become complex.

### 2. Decorator-Based Handler Registration

**Decision:** Use `@command_handler(CommandType)` instead of manual bus configuration.

**Why:** Handlers register themselves at import time. No central configuration file to maintain. Adding a new command is just: create the dataclass, create the handler, import it in `main.py`.

### 3. Request Pipeline Over Middleware

**Decision:** Per-route flow composition instead of global middleware.

**Why:** Different routes have different needs. A health check shouldn't run through authentication. A public registration endpoint needs logging but not permission checks. Flows make this explicit.

### 4. Domain Errors Over HTTP Exceptions

**Decision:** Domain raises `NotFoundError`, not `HTTPException(404)`.

**Why:** The domain layer doesn't know about HTTP. By raising domain-specific errors and mapping them to HTTP in the interfaces layer, the domain stays portable and testable.

### 5. Pydantic for Schemas Only

**Decision:** Use Pydantic for HTTP schemas and configuration, not for domain entities.

**Why:** Domain entities need custom validation logic, factory methods, and mutation rules that don't fit Pydantic's model. Keeping entities as plain Python classes with explicit validation gives full control.
