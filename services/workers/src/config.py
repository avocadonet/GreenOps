import os
from dataclasses import dataclass


@dataclass
class Config:
    database_url: str
    kafka_bootstrap_servers: str


def get_config() -> Config:
    return Config(
        database_url=os.environ["DATABASE_URL"],
        kafka_bootstrap_servers=os.environ["KAFKA_BOOTSTRAP_SERVERS"],
    )
