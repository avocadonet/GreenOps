from functools import wraps
from inspect import getcallargs

from sqlalchemy.exc import IntegrityError, NoResultFound

from ..config import SqlalchemyConfig
from .gateway import AsyncSqlAlchemyGateway


class SqlAlchemyRepository[CreateDto, Entity, Model]:
    config: SqlalchemyConfig[CreateDto, Entity, Model]
    gateway: AsyncSqlAlchemyGateway[Model]


class ErrorHandlingSqlAlchemyRepository[CreateDto, Entity, Model](
    SqlAlchemyRepository[CreateDto, Entity, Model]
):
    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if not callable(attr):
            return attr

        @wraps(attr)
        async def wrapper(*args, **kwargs):
            params = getcallargs(attr, *args, **kwargs)
            if params.get("self") is not None:
                params.pop("self")

            try:
                result = attr(*args, **kwargs)
                if hasattr(result, "__await__"):
                    return await result
                return result
            except NoResultFound as e:
                raise self.config.not_found(**params) from e
            except IntegrityError as e:
                error_mess = str(e).lower()
                params["original_exception"] = 3
                if "unique constraint" in error_mess:
                    raise self.config.unique_constraint_failed(**params) from e
                if "duplicate key" in error_mess:
                    raise self.config.duplicate_key(**params) from e
                raise e
            except Exception as e:
                raise e

        return wrapper


def provide[CreateDto, Entity, Model](
    config: SqlalchemyConfig[CreateDto, Entity, Model],
):
    def decorator(cls: type[SqlAlchemyRepository]) -> type[SqlAlchemyRepository]:
        cls.config = config
        return cls

    return decorator
