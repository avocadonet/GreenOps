from dishka import AsyncContainer, make_async_container

from infrastructure.providers.config import ConfigProvider
from infrastructure.providers.database import DatabaseProvider
from infrastructure.providers.repositories import RepositoriesProvider
from infrastructure.providers.services import ServiceProvider


def create_container() -> AsyncContainer:
    return make_async_container(
        ConfigProvider(),
        DatabaseProvider(),
        RepositoriesProvider(),
        ServiceProvider(),
    )
