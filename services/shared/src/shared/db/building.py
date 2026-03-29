from uuid import UUID, uuid4

from sqlalchemy import Enum as SAEnum, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.base import Base
from shared.enums import BuildingType


class BuildingModel(Base):
    __tablename__ = "buildings"

    building_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    address: Mapped[str] = mapped_column(String(500))
    building_type: Mapped[BuildingType] = mapped_column(
        SAEnum(BuildingType, name="building_type_enum")
    )
    total_area: Mapped[float]
