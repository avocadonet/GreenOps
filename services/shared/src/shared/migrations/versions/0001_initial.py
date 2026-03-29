"""initial — create all tables

Revision ID: 0001
Revises:
Create Date: 2026-03-29
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

# Enum type definitions — values must stay in sync with shared/enums.py
building_type_enum = sa.Enum("residential", "industrial", name="building_type_enum")
sensor_type_enum = sa.Enum("common", "individual", name="sensor_type_enum")
threshold_type_enum = sa.Enum("upper", "lower", name="threshold_type_enum")
tariff_zone_enum = sa.Enum("day", "night", name="tariff_zone_enum")
window_size_enum = sa.Enum("hour", "day", name="window_size_enum")
incident_type_enum = sa.Enum("overload", "leak", "idle", name="incident_type_enum")
incident_severity_enum = sa.Enum("low", "high", name="incident_severity_enum")
incident_status_enum = sa.Enum("open", "resolved", name="incident_status_enum")


def upgrade() -> None:
    # 1. buildings — no foreign keys
    op.create_table(
        "buildings",
        sa.Column("building_id", sa.UUID(), primary_key=True),
        sa.Column("address", sa.String(500), nullable=False),
        sa.Column("building_type", building_type_enum, nullable=False),
        sa.Column("total_area", sa.Float(), nullable=False),
    )

    # 2. units — FK → buildings
    op.create_table(
        "units",
        sa.Column("unit_id", sa.UUID(), primary_key=True),
        sa.Column("building_id", sa.UUID(), sa.ForeignKey("buildings.building_id"), nullable=False),
        sa.Column("unit_number", sa.String(50), nullable=False),
        sa.Column("floor", sa.Integer(), nullable=False),
        sa.Column("owner_name", sa.String(200), nullable=False),
    )

    # 3. sensors — FK → buildings (nullable), FK → units (nullable)
    op.create_table(
        "sensors",
        sa.Column("sensor_id", sa.UUID(), primary_key=True),
        sa.Column("serial_number", sa.String(100), nullable=False, unique=True),
        sa.Column("model", sa.String(200), nullable=False),
        sa.Column("calibration_date", sa.Date(), nullable=False),
        sa.Column("sensor_type", sensor_type_enum, nullable=False),
        sa.Column("building_id", sa.UUID(), sa.ForeignKey("buildings.building_id"), nullable=True),
        sa.Column("unit_id", sa.UUID(), sa.ForeignKey("units.unit_id"), nullable=True),
    )

    # 4. thresholds — FK → sensors
    op.create_table(
        "thresholds",
        sa.Column("threshold_id", sa.UUID(), primary_key=True),
        sa.Column("sensor_id", sa.UUID(), sa.ForeignKey("sensors.sensor_id"), nullable=False),
        sa.Column("limit_value", sa.Float(), nullable=False),
        sa.Column("threshold_type", threshold_type_enum, nullable=False),
        sa.Column("tariff_zone", tariff_zone_enum, nullable=False),
    )

    # 5. metrics — FK → sensors
    op.create_table(
        "metrics",
        sa.Column("metric_id", sa.UUID(), primary_key=True),
        sa.Column("sensor_id", sa.UUID(), sa.ForeignKey("sensors.sensor_id"), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.Column("measurement_unit", sa.String(10), nullable=False, server_default="kWh"),
        sa.Column("voltage", sa.Float(), nullable=False),
        sa.Column("current", sa.Float(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 6. energy_balances — FK → buildings
    op.create_table(
        "energy_balances",
        sa.Column("balance_id", sa.UUID(), primary_key=True),
        sa.Column("building_id", sa.UUID(), sa.ForeignKey("buildings.building_id"), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("loss_kwh", sa.Float(), nullable=False),
        sa.Column("loss_percent", sa.Float(), nullable=False),
    )

    # 7. average_loads — FK → sensors
    op.create_table(
        "average_loads",
        sa.Column("avg_load_id", sa.UUID(), primary_key=True),
        sa.Column("sensor_id", sa.UUID(), sa.ForeignKey("sensors.sensor_id"), nullable=False),
        sa.Column("window_size", window_size_enum, nullable=False),
        sa.Column("mean_value", sa.Float(), nullable=False),
        sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 8. peak_loads — FK → sensors
    op.create_table(
        "peak_loads",
        sa.Column("peak_id", sa.UUID(), primary_key=True),
        sa.Column("sensor_id", sa.UUID(), sa.ForeignKey("sensors.sensor_id"), nullable=False),
        sa.Column("max_value", sa.Float(), nullable=False),
        sa.Column("duration_seconds", sa.Float(), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 9. incidents — FK → thresholds (nullable), FK → peak_loads (nullable)
    op.create_table(
        "incidents",
        sa.Column("incident_id", sa.UUID(), primary_key=True),
        sa.Column("incident_type", incident_type_enum, nullable=False),
        sa.Column("severity", incident_severity_enum, nullable=False),
        sa.Column("status", incident_status_enum, nullable=False, server_default="open"),
        sa.Column("threshold_id", sa.UUID(), sa.ForeignKey("thresholds.threshold_id"), nullable=True),
        sa.Column("peak_load_id", sa.UUID(), sa.ForeignKey("peak_loads.peak_id"), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("incidents")
    op.drop_table("peak_loads")
    op.drop_table("average_loads")
    op.drop_table("energy_balances")
    op.drop_table("metrics")
    op.drop_table("thresholds")
    op.drop_table("sensors")
    op.drop_table("units")
    op.drop_table("buildings")

    incident_status_enum.drop(op.get_bind())
    incident_severity_enum.drop(op.get_bind())
    incident_type_enum.drop(op.get_bind())
    window_size_enum.drop(op.get_bind())
    tariff_zone_enum.drop(op.get_bind())
    threshold_type_enum.drop(op.get_bind())
    sensor_type_enum.drop(op.get_bind())
    building_type_enum.drop(op.get_bind())
