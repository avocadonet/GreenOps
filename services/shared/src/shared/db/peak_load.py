from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.base import Base


class PeakLoadModel(Base):
    __tablename__ = "peak_loads"

    peak_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    sensor_id: Mapped[UUID] = mapped_column(
        ForeignKey("sensors.sensor_id", ondelete="CASCADE")
    )
    max_value: Mapped[float]
    duration_seconds: Mapped[float]
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
