from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import Enum as SAEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.base import Base
from shared.enums import SensorType


class SensorModel(Base):
    __tablename__ = "sensors"

    sensor_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    serial_number: Mapped[str] = mapped_column(String(100), unique=True)
    model: Mapped[str] = mapped_column(String(200))
    calibration_date: Mapped[date]
    sensor_type: Mapped[SensorType] = mapped_column(
        SAEnum(SensorType, name="sensor_type_enum")
    )
    # Exactly one of building_id / unit_id must be set.
    # The XOR constraint is enforced in the service layer (MVP trade-off).
    building_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("buildings.building_id"), nullable=True
    )
    unit_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("units.unit_id"), nullable=True
    )
