import os
from dataclasses import dataclass


@dataclass
class Config:
    database_url: str
    nats_url: str


def get_config() -> Config:
    return Config(
        database_url=os.environ["DATABASE_URL"],
        nats_url=os.environ["NATS_URL"],
    )
