from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.base import Base


class MetricModel(Base):
    __tablename__ = "metrics"

    metric_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    sensor_id: Mapped[UUID] = mapped_column(ForeignKey("sensors.sensor_id"))
    value: Mapped[float]
    measurement_unit: Mapped[str] = mapped_column(String(10), default="kWh")
    voltage: Mapped[float]
    current: Mapped[float]
    recorded_at: Mapped[datetime]
