from adaptix import P
from adaptix.conversion import ConversionRetort, allow_unlinked_optional

from shared.db.organization import OrganizationModel
from shared.dtos.organization import CreateOrganizationDTO
from shared.entities.organization import Organization

retort = ConversionRetort()

org__map_from_db = retort.get_converter(OrganizationModel, Organization)
org__map_to_db = retort.get_converter(Organization, OrganizationModel)
org__create_mapper = retort.get_converter(
    CreateOrganizationDTO,
    OrganizationModel,
    recipe=[
        allow_unlinked_optional(
            P[OrganizationModel].id, P[OrganizationModel].created_at
        )
    ],
)
# org__map_to_db is used for update/delete where entity is always read from DB first (id always set)
