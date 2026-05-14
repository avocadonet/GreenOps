"""add organizations

Revision ID: a3f1c8e2b490
Revises: 9159ab7f9c17
Create Date: 2026-05-02 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a3f1c8e2b490"
down_revision: Union[str, None] = "9159ab7f9c17"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            name=op.f("fk_organizations_owner_id_users"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_organizations")),
    )
    op.create_table(
        "user_organization_roles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_user_organization_roles_organization_id_organizations"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_user_organization_roles_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "user_id", "organization_id", name=op.f("pk_user_organization_roles")
        ),
    )
    op.add_column(
        "buildings",
        sa.Column("organization_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_buildings_organization_id_organizations"),
        "buildings",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.add_column(
        "units",
        sa.Column("organization_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_units_organization_id_organizations"),
        "units",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.add_column(
        "sensors",
        sa.Column("organization_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_sensors_organization_id_organizations"),
        "sensors",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.add_column(
        "thresholds",
        sa.Column("organization_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_thresholds_organization_id_organizations"),
        "thresholds",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("fk_thresholds_organization_id_organizations"),
        "thresholds",
        type_="foreignkey",
    )
    op.drop_column("thresholds", "organization_id")
    op.drop_constraint(
        op.f("fk_sensors_organization_id_organizations"), "sensors", type_="foreignkey"
    )
    op.drop_column("sensors", "organization_id")
    op.drop_constraint(
        op.f("fk_units_organization_id_organizations"), "units", type_="foreignkey"
    )
    op.drop_column("units", "organization_id")
    op.drop_constraint(
        op.f("fk_buildings_organization_id_organizations"),
        "buildings",
        type_="foreignkey",
    )
    op.drop_column("buildings", "organization_id")
    op.drop_table("user_organization_roles")
    op.drop_table("organizations")
