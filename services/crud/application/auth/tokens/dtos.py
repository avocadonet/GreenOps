from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class TokenPairDto:
    access_token: str
    refresh_token: str


@dataclass
class TokenInfoDto:
    subject: str
    user_id: UUID
    expires_in: datetime
