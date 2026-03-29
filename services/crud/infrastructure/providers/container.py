from dishka import AsyncContainer, Provider, make_async_container

from .config import Config, ConfigProvider, get_config
from .database import DatabaseProvider
from .gateways import GatewaysProvider
from .repositories import RepositoriesProvider
from .services import ServiceProvider


def get_container_infrastructure() -> list[Provider]:
    return [
        ConfigProvider(),
        GatewaysProvider(),
        DatabaseProvider(),
        RepositoriesProvider(),
    ]


def get_container_application() -> list[Provider]:
    return [
        ServiceProvider(),
    ]


def create_container() -> AsyncContainer:
    return make_async_container(
        *get_container_infrastructure(),
        *get_container_application(),
        context={Config: get_config()},
    )
