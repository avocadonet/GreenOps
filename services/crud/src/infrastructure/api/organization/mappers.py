from shared.dtos.organization import CreateOrganizationDTO, UpdateOrganizationDTO
from shared.entities.organization import Organization

from .schemas import (
    CreateOrganizationRequest,
    OrganizationResponse,
    UpdateOrganizationRequest,
)


def create_request_to_dto(
    request: CreateOrganizationRequest, owner_id: int
) -> CreateOrganizationDTO:
    return CreateOrganizationDTO(
        name=request.name,
        owner_id=owner_id,
        description=request.description,
        contact_email=request.contact_email,
    )


def update_request_to_dto(
    request: UpdateOrganizationRequest, org_id: int
) -> UpdateOrganizationDTO:
    return UpdateOrganizationDTO(
        id=org_id,
        name=request.name,
        description=request.description,
        contact_email=request.contact_email,
    )


def entity_to_response(entity: Organization) -> OrganizationResponse:
    return OrganizationResponse(
        id=entity.id,
        name=entity.name,
        owner_id=entity.owner_id,
        description=entity.description,
        contact_email=entity.contact_email,
        created_at=entity.created_at,
    )
