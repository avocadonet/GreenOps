from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.base import Base


class EnergyBalanceModel(Base):
    __tablename__ = "energy_balances"

    balance_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    building_id: Mapped[UUID] = mapped_column(ForeignKey("buildings.building_id"))
    period_start: Mapped[datetime]
    period_end: Mapped[datetime]
    loss_kwh: Mapped[float]
    loss_percent: Mapped[float]
