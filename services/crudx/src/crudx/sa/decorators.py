import warnings
from contextlib import contextmanager
from dataclasses import asdict, is_dataclass
from functools import wraps
from inspect import getcallargs
from typing import Any, Awaitable, Callable, Optional

from crudx.sa.gateway import SqlAlchemyRepository
from crudx.types import Page, PageSpec
from sqlalchemy import Select


@contextmanager
def _extinguish_exceptions(raise_if_missing: bool):
    try:
        yield None
    except Exception as e:
        if raise_if_missing:
            raise e


def create[Entity](func: Optional[Callable] = None) -> Callable:
    def decorator(method: Callable[..., Awaitable[Entity]]):
        @wraps(method)
        async def wrapper(self: SqlAlchemyRepository, payload: Any) -> Entity:
            model = self.config.create_mapper(payload)
            saved = await self.gateway.insert_one(model)
            return self.config.model_mapper(saved)

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def read[Entity](func: Optional[Callable] = None, *, raise_if_missing: bool = True):
    def decorator(method: Callable[..., Awaitable]):
        @wraps(method)
        async def wrapper(self: SqlAlchemyRepository, *args, **kwargs) -> Entity | None:
            params = getcallargs(method, self, *args, **kwargs)
            params.pop("self")

            model = None
            result = await method(self, **params)
            with _extinguish_exceptions(raise_if_missing):
                if result is None:
                    model = await self.gateway.select_by_fields_first(**params)
                if is_dataclass(result):
                    dto_as_dict = asdict(result)
                    model = await self.gateway.select_by_fields_first(**dto_as_dict)
                if isinstance(result, Select):
                    model = await self.gateway.select_by_query_first(result)

            return model and self.config.model_mapper(model)

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def update[Entity](func: Optional[Callable] = None, *, raise_if_missing: bool = True):
    def decorator(method: Callable[..., Awaitable[Entity]]):
        @wraps(method)
        async def wrapper(self: SqlAlchemyRepository, entity: Entity) -> Entity:
            model = self.config.entity_mapper(entity)

            with _extinguish_exceptions(raise_if_missing):
                updated = await self.gateway.update(model)

            if updated is None:
                warnings.warn(f"Trying to update non-existent entity: {model}")
                return None

            return self.config.model_mapper(updated)

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def delete[Entity](func: Optional[Callable] = None, *, raise_if_missing: bool = True):
    def decorator(method: Callable[..., Awaitable[bool]]):
        @wraps(method)
        async def wrapper(self: SqlAlchemyRepository, entity: Entity) -> Entity | None:
            model = self.config.entity_mapper(entity)

            with _extinguish_exceptions(raise_if_missing):
                deleted = await self.gateway.delete(model)

            return deleted and self.config.model_mapper(deleted)

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator


def read_all[Entity](func: Optional[Callable] = None):
    def decorator(method: Callable[..., Awaitable[Page[Entity]]]):
        async def wrapper(self: SqlAlchemyRepository, *args, **kwargs) -> list[Entity]:
            params = getcallargs(method, self, *args, **kwargs)
            params.pop("self")

            params["page"] = params.pop("page", 10)
            params["page_size"] = params.pop("page_size", 10)

            models = []
            result = await method(self, **params)
            with _extinguish_exceptions(False):
                if result is None:
                    models = await self.gateway.select_all(**params)
                if is_dataclass(result):
                    dto_as_dict = asdict(result)
                    models = await self.gateway.select_by_fields_all(**dto_as_dict)
                if isinstance(result, Select):
                    models = await self.gateway.select_by_query_all(
                        self.gateway.with_pagination(
                            result,
                            PageSpec(
                                page=params["page"], page_size=params["page_size"]
                            ),
                        )
                    )

            return list(self.config.model_mapper(m) for m in models)

        return wrapper

    if func is not None:
        return decorator(func)
    return decorator
