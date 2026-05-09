from uuid import UUID

from application.auth.enums import PermissionsEnum
from application.auth.permissions.builder import PermissionBuilder
from application.auth.permissions.org_provider import OrgPermissionProvider
from application.auth.permissions.user_provider import UserPermissionProvider
from application.transaction import TransactionsGateway
from domain.building.repository import BuildingRepository
from domain.users.entities import User
from domain.users.role_getter import RoleGetter
from shared.dtos.building import CreateBuildingDTO, UpdateBuildingDTO
from shared.entities.building import Building


class BuildingService:
    def __init__(
        self,
        repository: BuildingRepository,
        tx: TransactionsGateway,
        role_getter: RoleGetter,
    ) -> None:
        self._repository = repository
        self._tx = tx
        self._role_getter = role_getter

    def _check(self, user: User, *perms: PermissionsEnum) -> None:
        PermissionBuilder().providers(UserPermissionProvider(user)).add(*perms).apply()

    async def _check_org(self, user: User, organization_id: int, *perms: PermissionsEnum) -> None:
        org_role = await self._role_getter(user, organization_id)
        PermissionBuilder().providers(OrgPermissionProvider(org_role)).add(*perms).apply()

    async def list_all(self, user: User, organization_id: int | None, page: int, page_size: int) -> list[Building]:
        if organization_id is not None:
            await self._check_org(user, organization_id, PermissionsEnum.CAN_READ_BUILDING)
        else:
            self._check(user, PermissionsEnum.CAN_READ_BUILDING)
        return await self._repository.list_all(organization_id, page, page_size)

    async def create(self, user: User, dto: CreateBuildingDTO) -> Building:
        if dto.organization_id is not None:
            await self._check_org(user, dto.organization_id, PermissionsEnum.CAN_CREATE_BUILDING)
        else:
            self._check(user, PermissionsEnum.CAN_CREATE_BUILDING)
        return await self._repository.create(dto)

    async def read(self, user: User, building_id: UUID) -> Building:
        building = await self._repository.read(building_id)
        if building.organization_id is not None:
            await self._check_org(user, building.organization_id, PermissionsEnum.CAN_READ_BUILDING)
        else:
            self._check(user, PermissionsEnum.CAN_READ_BUILDING)
        return building

    async def update(self, user: User, dto: UpdateBuildingDTO) -> Building:
        async with self._tx:
            building = await self._repository.read(dto.building_id)
            if building.organization_id is not None:
                await self._check_org(user, building.organization_id, PermissionsEnum.CAN_UPDATE_BUILDING)
            else:
                self._check(user, PermissionsEnum.CAN_UPDATE_BUILDING)
            building.address = dto.address
            building.total_area = dto.total_area
            return await self._repository.update(building)

    async def delete(self, user: User, building_id: UUID) -> Building:
        async with self._tx:
            building = await self._repository.read(building_id)
            if building.organization_id is not None:
                await self._check_org(user, building.organization_id, PermissionsEnum.CAN_DELETE_BUILDING)
            else:
                self._check(user, PermissionsEnum.CAN_DELETE_BUILDING)
            return await self._repository.delete(building)
