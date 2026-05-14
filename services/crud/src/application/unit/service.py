from uuid import UUID

from application.auth.enums import PermissionsEnum
from application.auth.permissions.builder import PermissionBuilder
from application.auth.permissions.org_provider import OrgPermissionProvider
from application.auth.permissions.user_provider import UserPermissionProvider
from application.transaction import TransactionsGateway
from domain.unit.repository import UnitRepository
from domain.users.entities import User
from domain.users.role_getter import RoleGetter
from shared.dtos.unit import CreateUnitDTO, UpdateUnitDTO
from shared.entities.unit import Unit


class UnitService:
    def __init__(
        self,
        repository: UnitRepository,
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

    async def list_all(self, user: User, building_id: UUID | None, organization_id: int | None, page: int, page_size: int) -> list[Unit]:
        if organization_id is not None:
            await self._check_org(user, organization_id, PermissionsEnum.CAN_READ_UNIT)
        else:
            self._check(user, PermissionsEnum.CAN_READ_UNIT)
        return await self._repository.list_all(building_id, organization_id, page, page_size)

    async def create(self, user: User, dto: CreateUnitDTO) -> Unit:
        if dto.organization_id is not None:
            await self._check_org(user, dto.organization_id, PermissionsEnum.CAN_CREATE_UNIT)
        else:
            self._check(user, PermissionsEnum.CAN_CREATE_UNIT)
        return await self._repository.create(dto)

    async def read(self, user: User, unit_id: UUID) -> Unit:
        unit = await self._repository.read(unit_id)
        if unit.organization_id is not None:
            await self._check_org(user, unit.organization_id, PermissionsEnum.CAN_READ_UNIT)
        else:
            self._check(user, PermissionsEnum.CAN_READ_UNIT)
        return unit

    async def update(self, user: User, dto: UpdateUnitDTO) -> Unit:
        async with self._tx:
            unit = await self._repository.read(dto.unit_id)
            if unit.organization_id is not None:
                await self._check_org(user, unit.organization_id, PermissionsEnum.CAN_UPDATE_UNIT)
            else:
                self._check(user, PermissionsEnum.CAN_UPDATE_UNIT)
            unit.unit_number = dto.unit_number
            unit.floor = dto.floor
            unit.owner_name = dto.owner_name
            return await self._repository.update(unit)

    async def delete(self, user: User, unit_id: UUID) -> Unit:
        async with self._tx:
            unit = await self._repository.read(unit_id)
            if unit.organization_id is not None:
                await self._check_org(user, unit.organization_id, PermissionsEnum.CAN_DELETE_UNIT)
            else:
                self._check(user, PermissionsEnum.CAN_DELETE_UNIT)
            return await self._repository.delete(unit)
