"""Persiste l'ordre des séries d'une séance.

Revision ID: 20260820_04
Revises: 20260819_03
Create Date: 2026-08-20
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260820_04"
down_revision = "20260819_03"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    if connection.dialect.name != "postgresql":
        return

    columns = {column["name"] for column in sa.inspect(connection).get_columns("training_sets")}
    if "position" not in columns:
        op.add_column("training_sets", sa.Column("position", sa.Integer(), nullable=True))

    # Aucun ordre métier n'était stocké auparavant. L'identifiant fournit un
    # classement déterministe aux données historiques ; tout nouvel écrit est
    # ensuite numéroté selon l'ordre reçu par l'API.
    connection.execute(
        sa.text(
            """
            WITH ranked AS (
                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        PARTITION BY workout_id
                        ORDER BY position ASC NULLS LAST, id ASC
                    ) - 1 AS stable_position
                FROM training_sets
            )
            UPDATE training_sets AS training_set
            SET position = ranked.stable_position
            FROM ranked
            WHERE training_set.id = ranked.id
            """
        )
    )
    op.alter_column("training_sets", "position", existing_type=sa.Integer(), nullable=False)

    inspector = sa.inspect(connection)
    checks = {constraint["name"] for constraint in inspector.get_check_constraints("training_sets")}
    if "ck_training_sets_position" not in checks:
        op.execute(
            sa.text(
                "ALTER TABLE training_sets ADD CONSTRAINT ck_training_sets_position "
                "CHECK (position >= 0) NOT VALID"
            )
        )
        op.execute(sa.text("ALTER TABLE training_sets VALIDATE CONSTRAINT ck_training_sets_position"))

    unique_constraints = {
        constraint["name"] for constraint in sa.inspect(connection).get_unique_constraints("training_sets")
    }
    if "uq_training_sets_workout_position" not in unique_constraints:
        op.create_unique_constraint(
            "uq_training_sets_workout_position",
            "training_sets",
            ["workout_id", "position"],
        )


def downgrade() -> None:
    connection = op.get_bind()
    if connection.dialect.name != "postgresql":
        return

    inspector = sa.inspect(connection)
    unique_constraints = {
        constraint["name"] for constraint in inspector.get_unique_constraints("training_sets")
    }
    if "uq_training_sets_workout_position" in unique_constraints:
        op.drop_constraint("uq_training_sets_workout_position", "training_sets", type_="unique")

    checks = {
        constraint["name"] for constraint in sa.inspect(connection).get_check_constraints("training_sets")
    }
    if "ck_training_sets_position" in checks:
        op.drop_constraint("ck_training_sets_position", "training_sets", type_="check")

    columns = {column["name"] for column in sa.inspect(connection).get_columns("training_sets")}
    if "position" in columns:
        op.drop_column("training_sets", "position")
