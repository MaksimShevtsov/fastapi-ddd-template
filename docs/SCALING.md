# Scaling Guide

This document describes how the architecture in this template can grow -- from a single process to a distributed system. Each stage builds on the previous one. The key point: the pure-SQL + CQRS foundation makes later stages possible without rewriting earlier code.

---

## Stage 1: Single Service (Day 1)

```
┌──────────────┐     ┌────────────┐
│   Uvicorn    │────>│  SQLite /  │
│   (1 worker) │     │  PostgreSQL│
└──────────────┘     └────────────┘
```

**What you have:** One process, one database. The template gives you this.

**When this is enough:** Most services. Seriously. A single FastAPI process on a modern server handles thousands of requests per second. SQLite handles millions of rows. Don't scale until you have evidence you need to.

**Bottleneck signals:**
- CPU utilization consistently above 70%
- Response latency creeping up under load
- Database connection pool exhausted

---

## Stage 2: Horizontal Scaling

```
                  ┌──────────────┐
              ┌──>│  Uvicorn #1  │──┐
┌──────────┐  │   └──────────────┘  │   ┌────────────┐
│   Load   │──┤                     ├──>│ PostgreSQL  │
│ Balancer │  │   ┌──────────────┐  │   └────────────┘
└──────────┘  └──>│  Uvicorn #2  │──┘
                  └──────────────┘
```

**What changes:** Add more workers behind a load balancer. Nothing in the code changes.

**Why it works:** The API layer is stateless by design:
- **JWT tokens** are self-contained -- any instance can validate them
- **No server-side sessions for the API** -- no sticky sessions needed
- **Database is the single source of truth** -- all instances share it

> **Note on the admin panel:** The admin panel uses cookie-based sessions (signed with `itsdangerous`). By default, session data is stored in the cookie itself (no server-side state), so it also works across multiple instances without sticky sessions. If you move to server-side session storage later, you'll need a shared session store (Redis, database).

**How to do it:**

```yaml
# docker-compose.prod.yml
services:
  app:
    deploy:
      replicas: 4
    command: uvicorn app.main:app --host 0.0.0.0 --workers 4
```

Or with Kubernetes:
```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 4
  template:
    spec:
      containers:
        - name: app
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
```

**Bottleneck signals for next stage:**
- Database becomes the bottleneck (high read load)
- Read queries are 10x more frequent than writes
- You need sub-millisecond read latency for some queries

---

## Stage 3: Read/Write Separation

```
                                 ┌──────────────┐
              ┌─ writes ────────>│   Primary    │
              │                  │  PostgreSQL   │──── replication ───┐
┌──────────┐  │                  └──────────────┘                    │
│   App    │──┤                                                      ▼
│ Instance │  │                  ┌──────────────┐    ┌──────────────┐
└──────────┘  └─ reads ─────────>│  Read Replica│    │ Read Replica │
                                 └──────────────┘    └──────────────┘
```

**What changes:** CQRS makes this trivial. Command handlers write to the primary. Query handlers read from replicas.

**Implementation:**

```python
# In your DI container, provide two engines:
def get_write_engine(request: Request) -> AsyncEngine:
    return request.app.state.write_engine

def get_read_engine(request: Request) -> AsyncEngine:
    return request.app.state.read_engine

# Command handlers receive the write engine (via UnitOfWork)
@command_handler(CreateUserCommand)
async def handle(command, uow):  # uow uses write_engine
    ...

# Query handlers receive the read engine
@query_handler(GetUserQuery)
async def handle(query, engine):  # engine is read_engine
    ...
```

The application code doesn't change. Only the DI wiring changes.

**Optional: Add caching for hot queries:**

```python
@query_handler(GetUserQuery)
async def handle(query: GetUserQuery, engine, cache):
    cached = await cache.get(f"user:{query.user_id}")
    if cached:
        return UserReadModel.model_validate_json(cached)

    row = await engine.fetch_one("users.get_by_id", {"id": query.user_id})
    if not row:
        raise NotFoundError(code="USER_NOT_FOUND", message="User not found")

    model = UserReadModel(**row)
    await cache.set(f"user:{query.user_id}", model.model_dump_json(), ex=300)
    return model
```

**Bottleneck signals for next stage:**
- One bounded context dominates resource usage
- Teams step on each other's code
- Different parts of the system need different scaling profiles

---

## Stage 4: Service Decomposition

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   Auth Service   │     │  Order Service    │     │  Payment Service │
│                  │     │                   │     │                  │
│  domain/         │     │  domain/          │     │  domain/         │
│  application/    │     │  application/     │     │  application/    │
│  infrastructure/ │     │  infrastructure/  │     │  infrastructure/ │
│  interfaces/     │     │  interfaces/      │     │  interfaces/     │
│       │          │     │       │           │     │       │          │
│    ┌──▼──┐       │     │    ┌──▼──┐        │     │    ┌──▼──┐       │
│    │ DB  │       │     │    │ DB  │        │     │    │ DB  │       │
│    └─────┘       │     │    └─────┘        │     │    └─────┘       │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

**What changes:** Each bounded context becomes its own service with its own database.

**Why the architecture supports this:** The 4-layer structure is already organized by bounded context. Each `domain/entities/`, `application/commands/`, and `infrastructure/db/repositories/` module is self-contained. Extracting a bounded context means:

1. Copy the relevant domain entities, commands, queries, and handlers
2. Copy the relevant repository implementations and SQL files
3. Create a new FastAPI app with just those routes
4. Point it at its own database

**What you need to add:**
- **API gateway** to route requests to the correct service
- **Service-to-service communication** (HTTP or async messaging)
- **Distributed tracing** (correlation IDs in the logging stage)

**Example: Extracting the Auth service:**

```
auth-service/
├── app/
│   ├── domain/
│   │   ├── entities/user.py          # Copied from monolith
│   │   ├── value_objects/user_id.py
│   │   └── errors.py
│   ├── application/
│   │   ├── commands/login.py, register.py, ...
│   │   └── handlers/commands/login_handler.py, ...
│   ├── infrastructure/
│   │   ├── db/repositories/user_repository.py
│   │   └── sql/users/
│   └── interfaces/
│       └── api/routes/auth.py
└── pyproject.toml
```

---

## Stage 5: Event-Driven Architecture

```
┌────────────┐    ┌──────────────┐    ┌─────────────┐
│   Auth     │───>│   Message    │───>│   Order     │
│   Service  │    │   Broker     │    │   Service   │
└────────────┘    │  (RabbitMQ,  │    └─────────────┘
                  │   Kafka,     │
┌────────────┐    │   Redis      │    ┌─────────────┐
│  Payment   │<───│   Streams)   │<───│ Notification│
│  Service   │    │              │    │   Service   │
└────────────┘    └──────────────┘    └─────────────┘
```

**What changes:** Services communicate via domain events instead of synchronous HTTP calls.

**How to add domain events to the existing architecture:**

```python
# 1. Define domain events
@dataclass(frozen=True)
class UserRegistered:
    user_id: str
    email: str
    registered_at: str

# 2. Collect events in the entity
class UserEntity(Entity[UserId]):
    def __init__(self, ...):
        ...
        self._events: list = []

    @classmethod
    def create(cls, ...) -> UserEntity:
        user = cls(...)
        user._events.append(UserRegistered(
            user_id=str(user.id_.value),
            email=user.email,
            registered_at=user.created_at.isoformat(),
        ))
        return user

    def collect_events(self) -> list:
        events = self._events.copy()
        self._events.clear()
        return events

# 3. Publish events after commit in the handler
@command_handler(RegisterUserCommand)
async def handle(command, uow, event_publisher):
    user = UserEntity.create(...)
    async with uow:
        await uow.user_repository.save(user)
    # Publish after successful commit
    for event in user.collect_events():
        await event_publisher.publish(event)

# 4. Other services subscribe
# notification-service/app/application/handlers/events/
@event_handler(UserRegistered)
async def handle_user_registered(event: UserRegistered):
    await send_welcome_email(event.email)
```

**Benefits:**
- Services are decoupled -- Auth doesn't know Notification exists
- Events can be replayed for debugging or rebuilding read models
- New consumers can be added without changing producers

---

## Scaling Decision Matrix

| Signal | Action |
|--------|--------|
| High CPU on single instance | Stage 2: Add workers |
| Database read bottleneck | Stage 3: Read replicas |
| Read latency too high | Stage 3: Add Redis cache layer |
| Teams blocking each other | Stage 4: Split into services |
| Synchronous calls creating cascading failures | Stage 5: Event-driven |
| Need audit trail / event sourcing | Stage 5: Domain events |

---

## Performance Targets

The template is designed for these baseline targets (single instance, PostgreSQL):

| Metric | Target |
|--------|--------|
| Health check latency (p99) | < 5ms |
| Authenticated read (p95) | < 50ms |
| Authenticated write (p95) | < 200ms |
| Startup time | < 5s |
| SQL queries per request | < 10 |

These are achievable because:
- **Async I/O** everywhere (FastAPI + asyncpg/aiosqlite)
- **Raw SQL** with no ORM overhead
- **No lazy loading** -- queries fetch exactly what they need
- **Connection pooling** via the database driver
