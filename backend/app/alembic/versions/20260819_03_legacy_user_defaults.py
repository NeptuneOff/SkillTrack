"""Ajoute les valeurs serveur requises par les colonnes historiques conservées.

Revision ID: 20260819_03
Revises: 20260819_02
Create Date: 2026-08-19
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260819_03"
down_revision = "20260819_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    if connection.dialect.name != "postgresql":
        return
    inspector = sa.inspect(connection)
    users = {column["name"] for column in inspector.get_columns("users")}
    if "is_active" in users:
        op.execute(sa.text("UPDATE users SET is_active = TRUE WHERE is_active IS NULL"))
        op.alter_column("users", "is_active", existing_type=sa.Boolean(), server_default=sa.true())
    if "updated_at" in users:
        op.alter_column(
            "users",
            "updated_at",
            existing_type=sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )
    workouts = {column["name"] for column in inspector.get_columns("workouts")}
    if "updated_at" in workouts:
        op.alter_column(
            "workouts",
            "updated_at",
            existing_type=sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
        )


def downgrade() -> None:
    # Les défauts rendent les anciennes colonnes compatibles sans supprimer ni
    # transformer de données ; les retirer recréerait volontairement la panne.
    pass
