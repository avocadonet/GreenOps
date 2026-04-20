from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.auth.dtos import CreateUserWithPasswordDto
from domain.users.dtos import ReadAllUsersDto
from domain.users.entities import User
from domain.users.exceptions import UserAlreadyExistsError, UserNotFoundError
from domain.users.repositories import UsersRepository
from shared.db.user import UserModel


def _model_to_entity(m: UserModel) -> User:
    from domain.users.enums import RoleEnum
    return User(
        id=m.id,
        email=m.email,
        fullname=m.fullname,
        is_active=m.is_active,
        hashed_password=m.hashed_password,
        salt=m.salt,
        telegram_id=m.telegram_id,
        created_at=m.created_at,
        role=RoleEnum(m.role),
    )


class UsersDatabaseRepository(UsersRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, dto: CreateUserWithPasswordDto) -> User:
        existing = await self._session.execute(
            select(UserModel).where(UserModel.email == dto.email)
        )
        if existing.scalar_one_or_none() is not None:
            raise UserAlreadyExistsError()
        model = UserModel(
            email=dto.email,
            fullname=dto.fullname,
            is_active=dto.is_active,
            hashed_password=dto.hashed_password,
            salt=dto.salt,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return _model_to_entity(model)

    async def read(self, user_id: int) -> User:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise UserNotFoundError()
        return _model_to_entity(model)

    async def read_by_email(self, email: str) -> User:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise UserNotFoundError()
        return _model_to_entity(model)

    async def read_all(self, dto: ReadAllUsersDto) -> list[User]:
        offset = (dto.page - 1) * dto.page_size
        result = await self._session.execute(
            select(UserModel).offset(offset).limit(dto.page_size)
        )
        return [_model_to_entity(m) for m in result.scalars().all()]

    async def read_by_ids(self, user_ids: list[int]) -> list[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id.in_(user_ids))
        )
        return [_model_to_entity(m) for m in result.scalars().all()]

    async def read_by_calendar_uuid(self, uuid: UUID) -> User:
        raise UserNotFoundError()

    async def update(self, user: User) -> User:
        await self._session.execute(
            update(UserModel)
            .where(UserModel.id == user.id)
            .values(
                fullname=user.fullname,
                is_active=user.is_active,
                hashed_password=user.hashed_password,
                salt=user.salt,
                telegram_id=user.telegram_id,
            )
        )
        return user

    async def delete(self, user: User) -> User:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise UserNotFoundError()
        await self._session.delete(model)
        return user

    async def change_user_active_status(self, user_id: int, status: bool) -> None:
        await self._session.execute(
            update(UserModel)
            .where(UserModel.id == user_id)
            .values(is_active=status)
        )

    async def get_super_user(self) -> User:
        from domain.users.enums import RoleEnum
        result = await self._session.execute(
            select(UserModel).where(UserModel.is_active == True).limit(1)
        )
        model = result.scalar_one_or_none()
        if model is None:
            raise UserNotFoundError()
        return _model_to_entity(model)
