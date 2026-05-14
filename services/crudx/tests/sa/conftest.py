import datetime as dt
from enum import Enum
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy import DateTime, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from conftest import RoleEnum, User


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(primary_key=True)
    fullname: Mapped[str]
    is_active: Mapped[bool]
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    salt: Mapped[str]
    hashed_password: Mapped[str]
    role: Mapped[str]

    def __repr__(self):
        return (
            "\nUser(id={},\n\temail={},\n\tfullname={}\n\t,is_active={}\n\t,"
            "created_at={},\n\tsalt={},\n\thashed_password={},\n\trole={})".format(
                self.id,
                self.email,
                self.fullname,
                self.is_active,
                self.created_at,
                self.salt,
                self.hashed_password,
                self.role,
            )
        )

    def __eq__(self, other):
        return (
            self.id == getattr(other, "id", None)
            and self.email == getattr(other, "email", None)
            and self.fullname == getattr(other, "fullname", None)
            and self.is_active == getattr(other, "is_active", None)
            and self.salt == getattr(other, "salt", None)
            and self.hashed_password == getattr(other, "hashed_password", None)
            and self.role == getattr(other, "role", None)
        )


@pytest.fixture
def mappers():
    def create_mapper(dto):
        if isinstance(dto, User):
            return dto
        return UserModel(**dto)

    def entity_mapper(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            fullname=entity.fullname,
            is_active=entity.is_active,
            created_at=entity.created_at,
            salt=entity.salt,
            hashed_password=entity.hashed_password,
            role=entity.role.value if isinstance(entity.role, Enum) else entity.role,
        )

    def model_mapper(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            fullname=model.fullname,
            is_active=model.is_active,
            created_at=model.created_at,
            salt=model.salt,
            hashed_password=model.hashed_password,
            role=RoleEnum(model.role),
        )

    return create_mapper, entity_mapper, model_mapper


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    sess = async_sessionmaker(engine, class_=AsyncSession)
    async with sess() as session:
        yield session
