class EntityException[Entity](Exception):
    pass


class EntityAccessDeniedException[Entity](EntityException[Entity]):
    def __init__(self, entity_type: type[Entity] | None = None):
        super().__init__(f"Access denied for entity: {entity_type.__name__}")


class EntityAlreadyExistsException[Entity](EntityException[Entity]):
    def __init__(self, entity_type: type[Entity] | None = None, **params):
        super().__init__(f"Entity already exists: {entity_type}, params: {params}")


class EntityNotFoundException[Entity](EntityException[Entity]):
    def __init__(self, entity_type: type[Entity] | None = None, **params):
        super().__init__(
            f"Entity not found: {entity_type.__class__.__name__}, params: {params}"
        )
