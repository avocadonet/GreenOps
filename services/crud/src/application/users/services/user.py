from fastapi import HTTPException

from domain.users.dtos import ReadAllUsersDto
from domain.users.entities import User
from domain.users.enums import RoleEnum, UserNotificationSendToEnum
from domain.users.exceptions import CalendarUUIDNotFoundError, TelegramNotConnectedError
from domain.users.repositories import UsersRepository, UserOrganizationRolesRepository

from application.transaction import TransactionsGateway
from application.users.dtos import UpdateUserDto


class UserService:
    def __init__(
        self,
        repository: UsersRepository,
        tx: TransactionsGateway,
        roles_repo: UserOrganizationRolesRepository,
    ):
        self._repository = repository
        self._tx = tx
        self._roles_repo = roles_repo

    async def get(self, user_id: int, actor: User = None) -> User:
        super_roles = {
            RoleEnum.SUPER_USER, 
            RoleEnum.SUPER_OWNER, 
            RoleEnum.SUPER_ADMIN, 
            RoleEnum.SUPER_REDACTOR
        }

        if actor and user_id != actor.id:
            if actor.role not in super_roles:
                raise HTTPException(
                    status_code=403, 
                    detail="Нет прав на просмотр чужого профиля"
                )       
        return await self._repository.read(user_id)

    async def list_all(self, dto: ReadAllUsersDto, actor: User) -> list[User]:
        super_roles = {
            RoleEnum.SUPER_USER,
            RoleEnum.SUPER_OWNER,
            RoleEnum.SUPER_ADMIN,
            RoleEnum.SUPER_REDACTOR,
        }

        if actor.role not in super_roles:
            raise HTTPException(
                status_code=403,
                detail="Доступ к списку всех пользователей запрещен"
            )

        return await self._repository.read_all(dto)

    async def get_by_ids(self, user_ids: list[int]) -> list[User]:
        return await self._repository.read_by_ids(user_ids)

    async def update(self, dto: UpdateUserDto, actor: User) -> User:
        async with self._tx:
            user = await self.get(dto.user_id)
            if dto.fullname:
                user.fullname = dto.fullname
            if dto.telegram_id:
                user.telegram_id = dto.telegram_id
            if dto.send_to_type:
                if (
                    user.telegram_id is None
                    and dto.send_to_type == UserNotificationSendToEnum.TELEGRAM
                ):
                    raise TelegramNotConnectedError
                user.settings.type = dto.send_to_type
            return await self._repository.update(user)

    async def delete(self, actor: User) -> User:
        async with self._tx:
            user = await self.get(actor.id)
            return await self._repository.delete(user)
