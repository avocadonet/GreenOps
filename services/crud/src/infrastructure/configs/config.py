import os
from dataclasses import dataclass


@dataclass
class Config:
    database_url: str
    jwt_secret_key: str


def get_config() -> Config:
    return Config(
        database_url=os.environ["DATABASE_URL"],
        jwt_secret_key=os.environ["JWT_SECRET_KEY"],
    )
