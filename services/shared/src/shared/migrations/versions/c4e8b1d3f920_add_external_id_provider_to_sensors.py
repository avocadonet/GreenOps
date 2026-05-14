"""add external_id and provider to sensors

Revision ID: c4e8b1d3f920
Revises: a3f1c8e2b490
Create Date: 2026-05-10 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c4e8b1d3f920"
down_revision: Union[str, None] = "a3f1c8e2b490"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("sensors", sa.Column("external_id", sa.String(length=128), nullable=True))
    op.add_column("sensors", sa.Column("provider", sa.String(length=64), nullable=True))
    op.create_unique_constraint(
        "uq_sensors_external_id_provider", "sensors", ["external_id", "provider"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_sensors_external_id_provider", "sensors", type_="unique")
    op.drop_column("sensors", "provider")
    op.drop_column("sensors", "external_id")
