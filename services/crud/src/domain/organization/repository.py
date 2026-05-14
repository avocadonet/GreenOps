from abc import ABCMeta, abstractmethod

from shared.dtos.organization import CreateOrganizationDTO, UpdateOrganizationDTO
from shared.entities.organization import Organization


class OrganizationRepository(metaclass=ABCMeta):
    @abstractmethod
    async def create(self, dto: CreateOrganizationDTO) -> Organization: ...

    @abstractmethod
    async def read(self, org_id: int) -> Organization: ...

    @abstractmethod
    async def list_all(self, page: int, page_size: int) -> list[Organization]: ...

    @abstractmethod
    async def update(self, org: Organization) -> Organization: ...

    @abstractmethod
    async def delete(self, org: Organization) -> Organization: ...
