from dataclasses import dataclass, field
from uuid import UUID, uuid4

from domain.users.entities import User


@dataclass
class ReadAllUsersDto:
    page: int
    page_size: int


@dataclass
class CreateTelegramTokenDto:
    user_id: int
    id: UUID = field(default_factory=uuid4)


@dataclass
class CreateActivationTokenDto:
    user_id: int
    user: User
    id: UUID = field(default_factory=uuid4)
