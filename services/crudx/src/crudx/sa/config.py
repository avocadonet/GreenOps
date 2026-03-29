from dataclasses import dataclass
from typing import Callable

from crudx.exceptions import (
    DuplicateKeyException,
    NotFoundException,
    UniqueConstraintFailedException,
)

ExcFactory = Callable[[...], Exception]


@dataclass
class SqlalchemyConfig[CreateDto, Entity, Model]:
    create_mapper: Callable[[CreateDto], Model] | Callable[[Entity], Model]
    entity_mapper: Callable[[Entity], Model]
    model_mapper: Callable[[Model], Entity]

    model: type[Model]

    not_found: ExcFactory = lambda *args, **kwargs: NotFoundException(**kwargs)
    unique_constraint_failed: ExcFactory = lambda *args, **kwargs: (
        UniqueConstraintFailedException(**kwargs)
    )
    duplicate_key: ExcFactory = lambda *args, **kwargs: DuplicateKeyException(**kwargs)
