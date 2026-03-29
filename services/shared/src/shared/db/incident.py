from uuid import UUID, uuid4

from sqlalchemy import Enum as SAEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from shared.db.base import Base
from shared.enums import IncidentSeverity, IncidentStatus, IncidentType


class IncidentModel(Base):
    __tablename__ = "incidents"

    incident_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    incident_type: Mapped[IncidentType] = mapped_column(
        SAEnum(IncidentType, name="incident_type_enum")
    )
    severity: Mapped[IncidentSeverity] = mapped_column(
        SAEnum(IncidentSeverity, name="incident_severity_enum")
    )
    status: Mapped[IncidentStatus] = mapped_column(
        SAEnum(IncidentStatus, name="incident_status_enum"),
        default=IncidentStatus.OPEN,
    )
    threshold_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("thresholds.threshold_id"), nullable=True
    )
    peak_load_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("peak_loads.peak_id"), nullable=True
    )
