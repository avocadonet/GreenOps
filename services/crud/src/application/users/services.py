from uuid import UUID

from domain.exceptions import EntityAccessDeniedException
from domain.auth.dtos import CreateUserDto, UpdateUserDto
from domain.auth.entities import User
from domain.auth.repositories import UsersRepository

from ..transaction import TransactionsGateway


class UsersService:
    def __init__(self, repository: UsersRepository, tx: TransactionsGateway):
        self._repository = repository
        self._transaction = tx

    async def create(self, dto: CreateUserDto) -> User:
        return await self._repository.create(dto)

    async def read(self, user_id: UUID, actor: User) -> User:
        user = await self._repository.read(user_id)
        self._check_access(actor=actor, entity=user)
        return user

    async def read_by_email(self, email: str) -> User:
        return await self._repository.read_by_email(email)

    async def update(self, dto: UpdateUserDto, actor: User) -> User:
        async with self._transaction:
            user = await self.read(dto.user_id, actor=actor)
            self._check_access(actor=actor, entity=user)
            user.is_active = dto.is_active
            return await self._repository.update(user)

    async def delete(self, user_id: UUID, actor: User) -> User:
        async with self._transaction:
            user = await self.read(user_id, actor=actor)
            self._check_access(actor=actor, entity=user)
            return await self._repository.delete(user)

    @staticmethod
    def _check_access(actor: User, entity: User):
        if actor.user_id != entity.user_id:
            raise EntityAccessDeniedException(User)
