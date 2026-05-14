from uuid import UUID

from application.auth.enums import PermissionsEnum
from application.auth.permissions.builder import PermissionBuilder
from application.auth.permissions.org_provider import OrgPermissionProvider
from application.auth.permissions.user_provider import UserPermissionProvider
from application.transaction import TransactionsGateway
from domain.threshold.repository import ThresholdRepository
from domain.users.entities import User
from domain.users.role_getter import RoleGetter
from shared.dtos.threshold import CreateThresholdDTO
from shared.entities.threshold import Threshold


class ThresholdService:
    def __init__(
        self,
        repository: ThresholdRepository,
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

    async def list_all(self, user: User, sensor_id: UUID | None, organization_id: int | None, page: int, page_size: int) -> list[Threshold]:
        if organization_id is not None:
            await self._check_org(user, organization_id, PermissionsEnum.CAN_READ_THRESHOLD)
            return await self._repository.list_all(sensor_id, organization_id, page, page_size)

        all_roles = await self._role_getter.all_roles(user)
        builder = PermissionBuilder().providers(
            UserPermissionProvider(user),
            *[OrgPermissionProvider(r) for r in all_roles],
        ).add(PermissionsEnum.CAN_READ_THRESHOLD)
        builder.apply()
        scope = builder.scope_for(PermissionsEnum.CAN_READ_THRESHOLD)

        items = await self._repository.list_all(sensor_id, None, page, page_size)
        if scope is not None:
            items = [t for t in items if t.organization_id in scope]
        return items

    async def create(self, user: User, dto: CreateThresholdDTO) -> Threshold:
        if dto.organization_id is not None:
            await self._check_org(user, dto.organization_id, PermissionsEnum.CAN_CREATE_THRESHOLD)
        else:
            self._check(user, PermissionsEnum.CAN_CREATE_THRESHOLD)
        return await self._repository.create(dto)

    async def read(self, user: User, threshold_id: UUID) -> Threshold:
        threshold = await self._repository.read(threshold_id)
        if threshold.organization_id is not None:
            await self._check_org(user, threshold.organization_id, PermissionsEnum.CAN_READ_THRESHOLD)
        else:
            self._check(user, PermissionsEnum.CAN_READ_THRESHOLD)
        return threshold

    async def update(self, user: User, threshold_id: UUID, limit_value: float) -> Threshold:
        async with self._tx:
            threshold = await self._repository.read(threshold_id)
            if threshold.organization_id is not None:
                await self._check_org(user, threshold.organization_id, PermissionsEnum.CAN_UPDATE_THRESHOLD)
            else:
                self._check(user, PermissionsEnum.CAN_UPDATE_THRESHOLD)
            threshold.limit_value = limit_value
            return await self._repository.update(threshold)

    async def delete(self, user: User, threshold_id: UUID) -> Threshold:
        async with self._tx:
            threshold = await self._repository.read(threshold_id)
            if threshold.organization_id is not None:
                await self._check_org(user, threshold.organization_id, PermissionsEnum.CAN_DELETE_THRESHOLD)
            else:
                self._check(user, PermissionsEnum.CAN_DELETE_THRESHOLD)
            return await self._repository.delete(threshold)
