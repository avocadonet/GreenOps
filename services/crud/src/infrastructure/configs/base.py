from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    cors_origins: list[str] = ["http://localhost:5173", "*"]
    server_host: str = "localhost"
    server_port: int = 5000
    secret_key: str
