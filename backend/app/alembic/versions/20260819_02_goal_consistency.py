"""Garantit la cohérence métier entre statut et achèvement d'un objectif.

Revision ID: 20260819_02
Revises: 20260819_01
Create Date: 2026-08-19
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260819_02"
down_revision = "20260819_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    if connection.dialect.name != "postgresql":
        return
    # L'ancien booléen reste la source de vérité lorsqu'il signalait déjà une
    # réussite ; ensuite le statut devient le champ canonique.
    connection.execute(
        sa.text("UPDATE goals SET status = 'termine' WHERE is_done IS TRUE AND status <> 'termine'")
    )
    connection.execute(sa.text("UPDATE goals SET is_done = (status = 'termine')"))

    checks = {constraint["name"] for constraint in sa.inspect(connection).get_check_constraints("goals")}
    if "ck_goals_completion_consistency" not in checks:
        op.execute(
            sa.text(
                "ALTER TABLE goals ADD CONSTRAINT ck_goals_completion_consistency "
                "CHECK (is_done = (status = 'termine')) NOT VALID"
            )
        )
        op.execute(sa.text("ALTER TABLE goals VALIDATE CONSTRAINT ck_goals_completion_consistency"))

    op.execute(
        sa.text(
            """
            CREATE OR REPLACE FUNCTION skilltrack_sync_goal_completion()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.is_done := (NEW.status = 'termine');
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql
            """
        )
    )
    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_goals_completion_consistency ON goals"))
    op.execute(
        sa.text(
            """
            CREATE TRIGGER trg_goals_completion_consistency
            BEFORE INSERT OR UPDATE OF status, is_done ON goals
            FOR EACH ROW EXECUTE FUNCTION skilltrack_sync_goal_completion()
            """
        )
    )


def downgrade() -> None:
    connection = op.get_bind()
    if connection.dialect.name != "postgresql":
        return
    op.execute(sa.text("DROP TRIGGER IF EXISTS trg_goals_completion_consistency ON goals"))
    op.execute(sa.text("DROP FUNCTION IF EXISTS skilltrack_sync_goal_completion()"))
    checks = {constraint["name"] for constraint in sa.inspect(connection).get_check_constraints("goals")}
    if "ck_goals_completion_consistency" in checks:
        op.drop_constraint("ck_goals_completion_consistency", "goals", type_="check")
