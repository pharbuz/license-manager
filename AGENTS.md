# AGENTS

## Frontend scope

For any work in `frontend/`, follow only `frontend/AGENTS.md`.
Do not apply frontend-specific instructions from this root `AGENTS.md` to files under `frontend/`.

## Formatting and linting

After each implementation, run these commands:

- .venv/bin/python -m black .
- .venv/bin/ruff check . --fix

If `black` is not available in `.venv`, install it inside that virtual environment (not globally), then run the commands above.

## Tests

After implementing any functionality, always add tests and run them.
If tests for the changed area already exist, update them so they match the current code behavior, then run them.

## Data models

When creating new data transfer or validation models, prefer Pydantic models over `dataclass` whenever possible.
Place Pydantic models in the appropriate domain-specific/model directories used by the project architecture.
All Celery tasks should accept and return Pydantic models instead of `dict` objects.

## Helpers and utilities

If you create simple helper functions that are likely reusable across the project, place them in the appropriate `helpers.py` module (or an existing analogous utilities module) instead of introducing `staticmethod`.

## Typing and attribute access

Use `getattr(...)` only when it is strictly necessary, for example when working with genuinely dynamic or partially unknown objects.
In all normal application code, prefer direct typed attribute access and explicit type declarations over defensive `getattr(...)` calls.
Never use `getattr(...)` on `UnitOfWork` objects, including `self._uow` and `self.uow`; access repositories on the unit of work directly and type the code accordingly.

## Celery integration checks

If you change anything in Celery tasks, verify whether `celery_app.py` and the tasks router file `tasks.py` also require updates.
When adding Pydantic models to Celery tasks, ensure the task decorator includes `pydantic=True`, for example:

```python
@shared_task(
    pydantic=True,
)
```
