from crudx.sa import decorators
from crudx.sa.config import SqlalchemyConfig
from crudx.sa.gateway import (
    AsyncSqlAlchemyGateway,
    ErrorHandlingSqlAlchemyRepository,
    provide,
)
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db.incident import IncidentModel
from shared.dtos.incident import CreateIncidentDTO
from shared.entities.incident import Incident

from . import mappers


@provide(
    SqlalchemyConfig[CreateIncidentDTO, Incident, IncidentModel](
        create_mapper=mappers.incident__create_mapper,
        entity_mapper=mappers.incident__map_to_db,
        model_mapper=mappers.incident__map_from_db,
        model=IncidentModel,
    )
)
class IncidentDatabaseRepository(
    ErrorHandlingSqlAlchemyRepository[CreateIncidentDTO, Incident, IncidentModel],
):
    def __init__(self, session: AsyncSession) -> None:
        self.gateway = AsyncSqlAlchemyGateway(
            session, sa_model=IncidentModel, id_attr="incident_id"
        )

    @decorators.create
    async def create(self, dto: CreateIncidentDTO) -> Incident: ...
