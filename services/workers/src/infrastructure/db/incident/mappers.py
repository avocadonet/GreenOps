from adaptix import P
from adaptix.conversion import ConversionRetort, allow_unlinked_optional

from shared.db.incident import IncidentModel
from shared.dtos.incident import CreateIncidentDTO
from shared.entities.incident import Incident

retort = ConversionRetort()

incident__map_from_db = retort.get_converter(IncidentModel, Incident)
incident__map_to_db = retort.get_converter(Incident, IncidentModel)
incident__create_mapper = retort.get_converter(
    CreateIncidentDTO,
    IncidentModel,
    recipe=[
        allow_unlinked_optional(P[IncidentModel].incident_id),
        allow_unlinked_optional(P[IncidentModel].status),
    ],
)
