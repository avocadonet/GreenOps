from application.auth.enums import PermissionsEnum
from application.auth.permissions.builder import PermissionBuilder
from application.auth.permissions.org_provider import OrgPermissionProvider
from application.auth.permissions.user_provider import UserPermissionProvider
from application.transaction import TransactionsGateway
from domain.organization.repository import OrganizationRepository
from domain.users.entities import User
from domain.users.role_getter import RoleGetter
from domain.exceptions import EntityAccessDenied
from shared.dtos.organization import CreateOrganizationDTO, UpdateOrganizationDTO
from shared.entities.organization import Organization


class OrganizationService:
    def __init__(
        self,
        repository: OrganizationRepository,
        tx: TransactionsGateway,
        role_getter: RoleGetter,
    ) -> None:
        self._repository = repository
        self._tx = tx
        self._role_getter = role_getter

    def _check(self, user: User, *perms: PermissionsEnum) -> None:
        PermissionBuilder().providers(UserPermissionProvider(user)).add(*perms).apply()

    async def _check_org(
        self, user: User, organization_id: int, *perms: PermissionsEnum
    ) -> None:
        org_role = await self._role_getter(user, organization_id)
        PermissionBuilder().providers(OrgPermissionProvider(org_role)).add(
            *perms
        ).apply()

    async def list_all(
        self, user: User, page: int, page_size: int
    ) -> list[Organization]:
        result = []
        async with self._tx:
            organizations = await self._repository.list_all(page, page_size)
            try:
                await self._check(user, PermissionsEnum.CAN_READ_ORGANIZATION)
                return organizations
            except EntityAccessDenied:
                pass

            for org in organizations:
                try:
                    await self._check_org(
                        user, org.id, PermissionsEnum.CAN_READ_ORGANIZATION
                    )
                    result.append(org)
                except EntityAccessDenied:
                    continue

            if len(result) == 0:
                raise EntityAccessDenied()

            return result

    async def create(self, user: User, dto: CreateOrganizationDTO) -> Organization:
        self._check(user, PermissionsEnum.CAN_CREATE_ORGANIZATION)
        return await self._repository.create(dto)

    async def read(self, user: User, org_id: int) -> Organization:
        org = await self._repository.read(org_id)
        await self._check_org(user, org_id, PermissionsEnum.CAN_READ_ORGANIZATION)
        return org

    async def update(self, user: User, dto: UpdateOrganizationDTO) -> Organization:
        async with self._tx:
            await self._check_org(user, dto.id, PermissionsEnum.CAN_UPDATE_ORGANIZATION)

            org = await self._repository.read(dto.id)
            org.name = dto.name
            org.description = dto.description
            org.contact_email = dto.contact_email
            return await self._repository.update(org)

    async def delete(self, user: User, org_id: int) -> Organization:
        async with self._tx:
            await self._check_org(user, org_id, PermissionsEnum.CAN_DELETE_ORGANIZATION)

            org = await self._repository.read(org_id)
            return await self._repository.delete(org)
