from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.base import Base
from shared.enums import WindowSize


class AverageLoadModel(Base):
    __tablename__ = "average_loads"

    avg_load_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    sensor_id: Mapped[UUID] = mapped_column(ForeignKey("sensors.sensor_id"))
    window_size: Mapped[WindowSize] = mapped_column(
        SAEnum(WindowSize, name="window_size_enum")
    )
    mean_value: Mapped[float]
    calculated_at: Mapped[datetime]
