from dataclasses import dataclass
from uuid import UUID
from domain.enums import UserRole

@dataclass
class Organization:
    org_id: UUID
    name: str
    is_active: bool

@dataclass
class User:
    user_id: UUID
    org_id: UUID          # Привязка к компании
    email: str
    hashed_password: str  # В домене мы оперируем уже хэшом
    role: UserRole
    is_active: bool
