# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Quickstart

{% if cookiecutter.use_docker -%}
### With Docker

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```
{%- else -%}
### Local Development

```bash
uv sync  # or: pip install -e '.[dev]'
uvicorn app.main:app --reload
```
{%- endif %}

Verify the service is running:

```bash
curl http://localhost:8000/health
# {"status": "healthy", "service": "{{ cookiecutter.project_name }}", "version": "0.1.0"}
```

## Project Structure

```
app/
├── domain/           # Domain models, entities, value objects (stdlib only)
│   ├── entities/     # Domain entities (e.g., UserEntity)
│   ├── value_objects/ # Value objects (e.g., UserId)
│   ├── interfaces/   # Abstract repository interfaces
│   └── errors.py     # Domain error hierarchy
├── application/      # Use cases, commands, queries, handlers
│   ├── commands/     # Command DTOs
│   ├── queries/      # Query DTOs
│   ├── handlers/     # Command and query handlers
│   ├── bus/          # CommandBus and QueryBus
│   ├── read_models/  # Read-optimized models (Pydantic)
│   ├── dto/          # Data transfer objects
│   └── unit_of_work.py  # UnitOfWork protocol
├── infrastructure/   # External concerns (DB, config, logging)
│   ├── config.py     # Pydantic Settings
│   ├── logging.py    # Structured JSON logging
│   ├── db/           # Database connection, repositories, UoW
│   └── sql/          # Raw SQL files organized by entity
└── interfaces/       # HTTP layer (routes, schemas, pipeline)
    ├── api/          # FastAPI routes and Pydantic schemas
    ├── dependencies/ # Dependency injection wiring
    └── pipeline/     # Request pipeline stages and flows
```

## CQRS: Adding a New Command (Write Operation)

1. **Define command** in `app/application/commands/`:
   ```python
   @dataclass(frozen=True)
   class CreateOrderCommand:
       customer_id: str
       items: list[str]
   ```

2. **Create domain entity** in `app/domain/entities/` (stdlib only):
   ```python
   @dataclass
   class OrderEntity:
       id: OrderId
       customer_id: str

       @classmethod
       def create(cls, customer_id: str) -> "OrderEntity":
           return cls(id=OrderId.generate(), customer_id=customer_id)
   ```

3. **Register handler** in `app/application/handlers/commands/`:
   ```python
   @command_handler(CreateOrderCommand)
   async def handle(command: CreateOrderCommand, uow: UnitOfWork) -> OrderDTO:
       order = OrderEntity.create(command.customer_id)
       async with uow:
           await uow.order_repository.save(order)
       return OrderDTO(id=str(order.id.value))
   ```

4. **Add route** in `app/interfaces/api/routes/`:
   ```python
   @router.post("/orders", status_code=201)
   async def create_order(
       request: CreateOrderRequest,
       ctx: RequestContext = Depends(flow_dependency(authenticated_flow)),
       bus: CommandBus = Depends(get_command_bus),
       uow: UnitOfWork = Depends(get_unit_of_work),
   ):
       return await bus.dispatch(CreateOrderCommand(...), uow=uow)
   ```

## CQRS: Adding a New Query (Read Operation)

1. **Define query** in `app/application/queries/`:
   ```python
   @dataclass(frozen=True)
   class GetOrderQuery:
       order_id: str
   ```

2. **Create read model** in `app/application/read_models/` (Pydantic):
   ```python
   class OrderReadModel(BaseModel):
       id: str
       customer_id: str
       created_at: str
   ```

3. **Add SQL file** in `app/infrastructure/sql/orders/get_by_id.sql`

4. **Register handler** in `app/application/handlers/queries/`:
   ```python
   @query_handler(GetOrderQuery)
   async def handle(query: GetOrderQuery, engine: AsyncEngine) -> OrderReadModel:
       result = await engine.fetch_one("orders.get_by_id", {"id": query.order_id})
       if not result:
           raise NotFoundError(code="ORDER_NOT_FOUND", message="Order not found")
       return OrderReadModel(**result)
   ```

## Pipeline Integration

Add custom pipeline stages by extending `FlowComponent`:

```python
class AuditStage(FlowComponent):
    category = ComponentCategory.CUSTOM

    async def resolve(self, ctx: RequestContext) -> None:
        logger.info(f"User {ctx.user.id} accessing {ctx.request.url}")
```

Compose stages into flows and wire to routes:

```python
audited_flow = Flow(JWTAuthentication(...), AuditStage())

@router.get("/sensitive")
async def get_sensitive(ctx: RequestContext = Depends(flow_dependency(audited_flow))):
    ...
```

## Error Handling

All errors follow a standardized envelope:

```json
{"error": {"code": "NOT_FOUND", "message": "User not found", "details": {}}}
```

| Status | Error Class | Use Case |
|--------|------------|----------|
| 400 | `DomainError` | Generic domain error |
| 404 | `NotFoundError` | Entity not found |
| 409 | `ConflictError` | Duplicate/conflict |
| 422 | `ValidationError` | Business rule violation |
| 500 | — | Unhandled exception (no details leaked) |

## Development

```bash
ruff check .    # lint
ruff format .   # format
pytest          # run tests
```
