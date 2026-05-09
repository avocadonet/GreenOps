from dataclasses import dataclass
from datetime import datetime


@dataclass
class Organization:
    id: int
    name: str
    owner_id: int
    created_at: datetime
    description: str | None = None
    contact_email: str | None = None
