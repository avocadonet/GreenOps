from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings


class PostgresConfig(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    postgres_db: str

    @computed_field
    @property
    def postgres_url(self) -> PostgresDsn:
        return PostgresDsn(
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
