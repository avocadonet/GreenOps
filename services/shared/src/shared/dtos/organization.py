from dataclasses import dataclass


@dataclass
class CreateOrganizationDTO:
    name: str
    owner_id: int
    description: str | None = None
    contact_email: str | None = None


@dataclass
class UpdateOrganizationDTO:
    id: int
    name: str
    description: str | None = None
    contact_email: str | None = None
