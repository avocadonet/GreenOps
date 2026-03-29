from functools import lru_cache
from pathlib import Path

from .base import BaseConfig
from .postgres import PostgresConfig

BASE_PATH = Path(__file__).parent.parent.parent.absolute()


class Config(PostgresConfig, BaseConfig):
    pass


@lru_cache
def get_config() -> Config:
    return Config()


__all__ = ["get_config", "Config", "BASE_PATH"]
