from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.base import Base


class UnitModel(Base):
    __tablename__ = "units"

    unit_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    building_id: Mapped[UUID] = mapped_column(
        ForeignKey("buildings.building_id", ondelete="CASCADE")
    )
    unit_number: Mapped[str] = mapped_column(String(50))
    floor: Mapped[int]
    owner_name: Mapped[str] = mapped_column(String(200))
    organization_id: Mapped[int | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True
    )
