from datetime import datetime

from pydantic import BaseModel


class CreateOrganizationRequest(BaseModel):
    name: str
    description: str | None = None
    contact_email: str | None = None


class UpdateOrganizationRequest(BaseModel):
    name: str
    description: str | None = None
    contact_email: str | None = None


class OrganizationResponse(BaseModel):
    id: int
    name: str
    owner_id: int
    description: str | None = None
    contact_email: str | None = None
    created_at: datetime | None = None
