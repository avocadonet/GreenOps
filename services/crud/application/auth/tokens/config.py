from dataclasses import dataclass
from datetime import timedelta


@dataclass
class TokenConfig:
    secret_key: str
    algorithm: str = "HS256"
    access_token_expires_time: timedelta = timedelta(hours=1)
    refresh_token_expires_time: timedelta = timedelta(days=30)
