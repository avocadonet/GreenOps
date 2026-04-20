"""add ON DELETE CASCADE / SET NULL to all foreign keys

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-20
"""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # units.building_id → CASCADE
    op.drop_constraint("units_building_id_fkey", "units", type_="foreignkey")
    op.create_foreign_key(
        "units_building_id_fkey",
        "units", "buildings",
        ["building_id"], ["building_id"],
        ondelete="CASCADE",
    )

    # sensors.building_id → CASCADE
    op.drop_constraint("sensors_building_id_fkey", "sensors", type_="foreignkey")
    op.create_foreign_key(
        "sensors_building_id_fkey",
        "sensors", "buildings",
        ["building_id"], ["building_id"],
        ondelete="CASCADE",
    )

    # sensors.unit_id → CASCADE
    op.drop_constraint("sensors_unit_id_fkey", "sensors", type_="foreignkey")
    op.create_foreign_key(
        "sensors_unit_id_fkey",
        "sensors", "units",
        ["unit_id"], ["unit_id"],
        ondelete="CASCADE",
    )

    # thresholds.sensor_id → CASCADE
    op.drop_constraint("thresholds_sensor_id_fkey", "thresholds", type_="foreignkey")
    op.create_foreign_key(
        "thresholds_sensor_id_fkey",
        "thresholds", "sensors",
        ["sensor_id"], ["sensor_id"],
        ondelete="CASCADE",
    )

    # metrics.sensor_id → CASCADE
    op.drop_constraint("metrics_sensor_id_fkey", "metrics", type_="foreignkey")
    op.create_foreign_key(
        "metrics_sensor_id_fkey",
        "metrics", "sensors",
        ["sensor_id"], ["sensor_id"],
        ondelete="CASCADE",
    )

    # energy_balances.building_id → CASCADE
    op.drop_constraint(
        "energy_balances_building_id_fkey", "energy_balances", type_="foreignkey"
    )
    op.create_foreign_key(
        "energy_balances_building_id_fkey",
        "energy_balances", "buildings",
        ["building_id"], ["building_id"],
        ondelete="CASCADE",
    )

    # average_loads.sensor_id → CASCADE
    op.drop_constraint(
        "average_loads_sensor_id_fkey", "average_loads", type_="foreignkey"
    )
    op.create_foreign_key(
        "average_loads_sensor_id_fkey",
        "average_loads", "sensors",
        ["sensor_id"], ["sensor_id"],
        ondelete="CASCADE",
    )

    # peak_loads.sensor_id → CASCADE
    op.drop_constraint("peak_loads_sensor_id_fkey", "peak_loads", type_="foreignkey")
    op.create_foreign_key(
        "peak_loads_sensor_id_fkey",
        "peak_loads", "sensors",
        ["sensor_id"], ["sensor_id"],
        ondelete="CASCADE",
    )

    # incidents.threshold_id → SET NULL (audit log must survive sensor deletion)
    op.drop_constraint(
        "incidents_threshold_id_fkey", "incidents", type_="foreignkey"
    )
    op.create_foreign_key(
        "incidents_threshold_id_fkey",
        "incidents", "thresholds",
        ["threshold_id"], ["threshold_id"],
        ondelete="SET NULL",
    )

    # incidents.peak_load_id → SET NULL
    op.drop_constraint(
        "incidents_peak_load_id_fkey", "incidents", type_="foreignkey"
    )
    op.create_foreign_key(
        "incidents_peak_load_id_fkey",
        "incidents", "peak_loads",
        ["peak_load_id"], ["peak_id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    # Restore all FKs to default RESTRICT behaviour

    op.drop_constraint("incidents_peak_load_id_fkey", "incidents", type_="foreignkey")
    op.create_foreign_key(
        "incidents_peak_load_id_fkey",
        "incidents", "peak_loads",
        ["peak_load_id"], ["peak_id"],
    )

    op.drop_constraint(
        "incidents_threshold_id_fkey", "incidents", type_="foreignkey"
    )
    op.create_foreign_key(
        "incidents_threshold_id_fkey",
        "incidents", "thresholds",
        ["threshold_id"], ["threshold_id"],
    )

    op.drop_constraint("peak_loads_sensor_id_fkey", "peak_loads", type_="foreignkey")
    op.create_foreign_key(
        "peak_loads_sensor_id_fkey",
        "peak_loads", "sensors",
        ["sensor_id"], ["sensor_id"],
    )

    op.drop_constraint(
        "average_loads_sensor_id_fkey", "average_loads", type_="foreignkey"
    )
    op.create_foreign_key(
        "average_loads_sensor_id_fkey",
        "average_loads", "sensors",
        ["sensor_id"], ["sensor_id"],
    )

    op.drop_constraint(
        "energy_balances_building_id_fkey", "energy_balances", type_="foreignkey"
    )
    op.create_foreign_key(
        "energy_balances_building_id_fkey",
        "energy_balances", "buildings",
        ["building_id"], ["building_id"],
    )

    op.drop_constraint("metrics_sensor_id_fkey", "metrics", type_="foreignkey")
    op.create_foreign_key(
        "metrics_sensor_id_fkey",
        "metrics", "sensors",
        ["sensor_id"], ["sensor_id"],
    )

    op.drop_constraint(
        "thresholds_sensor_id_fkey", "thresholds", type_="foreignkey"
    )
    op.create_foreign_key(
        "thresholds_sensor_id_fkey",
        "thresholds", "sensors",
        ["sensor_id"], ["sensor_id"],
    )

    op.drop_constraint("sensors_unit_id_fkey", "sensors", type_="foreignkey")
    op.create_foreign_key(
        "sensors_unit_id_fkey",
        "sensors", "units",
        ["unit_id"], ["unit_id"],
    )

    op.drop_constraint("sensors_building_id_fkey", "sensors", type_="foreignkey")
    op.create_foreign_key(
        "sensors_building_id_fkey",
        "sensors", "buildings",
        ["building_id"], ["building_id"],
    )

    op.drop_constraint("units_building_id_fkey", "units", type_="foreignkey")
    op.create_foreign_key(
        "units_building_id_fkey",
        "units", "buildings",
        ["building_id"], ["building_id"],
    )
