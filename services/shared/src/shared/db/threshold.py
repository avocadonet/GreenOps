from uuid import UUID, uuid4

from sqlalchemy import Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.base import Base
from shared.enums import TariffZone, ThresholdType


class ThresholdModel(Base):
    __tablename__ = "thresholds"

    threshold_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    sensor_id: Mapped[UUID] = mapped_column(ForeignKey("sensors.sensor_id"))
    limit_value: Mapped[float]
    threshold_type: Mapped[ThresholdType] = mapped_column(
        SAEnum(ThresholdType, name="threshold_type_enum")
    )
    tariff_zone: Mapped[TariffZone] = mapped_column(
        SAEnum(TariffZone, name="tariff_zone_enum")
    )
