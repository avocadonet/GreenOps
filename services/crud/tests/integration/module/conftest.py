from uuid import uuid4

import pytest
import pytest_asyncio
from application.auth.dtos import RegisterUserDto
from application.auth.services import AuthService
from application.auth.tokens.config import TokenConfig
from application.auth.tokens.gateways import SecurityGateway, TokensGateway
from application.transaction import TransactionsGateway
from application.users.services import UsersService
from domain.auth.dtos import CreateUserDto
from domain.auth.entities import User
from domain.auth.repositories import UsersRepository
from domain.enums import UserRole
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import infrastructure.providers.database  # noqa
from infrastructure.db.models import Base
from infrastructure.db.postgres import SqlalchemyTransactionsGateway
from infrastructure.db.users.repositories import UsersDatabaseRepository
from infrastructure.gateways.auth import BcryptSecurityGateway, JwtTokensGateway


@pytest_asyncio.fixture(scope="function")
async def engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncSession:
    sess = async_sessionmaker(engine, class_=AsyncSession)
    async with sess() as session:
        yield session


@pytest.fixture
def repo(session: AsyncSession) -> UsersRepository:
    return UsersDatabaseRepository(session=session)


@pytest.fixture
def transaction_gateway(session: AsyncSession) -> TransactionsGateway:
    return SqlalchemyTransactionsGateway(session=session)


@pytest.fixture
def users_service(
    repo: UsersDatabaseRepository, transaction_gateway: TransactionsGateway
):
    return UsersService(repo, transaction_gateway)


@pytest.fixture(scope="session")
def security_gateway() -> SecurityGateway:
    return BcryptSecurityGateway()


@pytest.fixture(scope="session")
def tokens_config() -> TokenConfig:
    return TokenConfig(secret_key="secret")


@pytest.fixture(scope="session")
def tokens_gateway(tokens_config: TokenConfig) -> TokensGateway:
    return JwtTokensGateway(tokens_config)


@pytest.fixture
def auth_service(
    tokens_gateway: TokensGateway,
    security_gateway: SecurityGateway,
    users_service: UsersService,
) -> AuthService:
    return AuthService(security_gateway, tokens_gateway, users_service)


@pytest.fixture(scope="session")
def register_user_dto() -> RegisterUserDto:
    return RegisterUserDto(
        email="email@email.com",
        password="Migger",
        org_id=uuid4(),
    )


@pytest_asyncio.fixture
async def created_user(
    register_user_dto: RegisterUserDto, auth_service: AuthService
) -> User:
    user, _ = await auth_service.register(register_user_dto)
    return user


@pytest_asyncio.fixture
async def create_user_dto(created_user: User) -> CreateUserDto:
    return CreateUserDto(
        email=created_user.email,
        hashed_password=created_user.hashed_password,
        org_id=created_user.org_id,
        role=created_user.role,
        is_active=created_user.is_active,
    )
