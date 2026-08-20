"""Adapte sans perte les volumes historiques au schéma canonique SkillTrack.

Revision ID: 20260819_01
Revises:
Create Date: 2026-08-19
"""

from __future__ import annotations

from collections.abc import Iterable

import sqlalchemy as sa
from alembic import op

from app.db import Base
from app import models  # noqa: F401

revision = "20260819_01"
down_revision = None
branch_labels = None
depends_on = None


def _columns(table: str) -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns(table)}


def _add_missing_columns(table: str, columns: dict[str, sa.Column]) -> None:
    existing = _columns(table)
    for name, column in columns.items():
        if name not in existing:
            op.add_column(table, column)


def _execute(statements: Iterable[str]) -> None:
    connection = op.get_bind()
    for statement in statements:
        connection.execute(sa.text(statement))


def _has_null(table: str, column: str) -> bool:
    result = op.get_bind().execute(sa.text(f'SELECT 1 FROM "{table}" WHERE "{column}" IS NULL LIMIT 1'))
    return result.first() is not None


def _ensure_not_null(table: str, column: str, existing_type: sa.types.TypeEngine) -> None:
    current = next(item for item in sa.inspect(op.get_bind()).get_columns(table) if item["name"] == column)
    if current.get("nullable", True) and not _has_null(table, column):
        op.alter_column(table, column, existing_type=existing_type, nullable=False)


def _ensure_index(table: str, name: str, columns: list[str], *, unique: bool = False) -> None:
    existing = {index["name"] for index in sa.inspect(op.get_bind()).get_indexes(table)}
    if name not in existing:
        op.create_index(name, table, columns, unique=unique)


def _ensure_cascade_fk(table: str, column: str, target_table: str, target_column: str, name: str) -> None:
    foreign_keys = sa.inspect(op.get_bind()).get_foreign_keys(table)
    matching = [fk for fk in foreign_keys if fk.get("constrained_columns") == [column]]
    if any(
        fk.get("referred_table") == target_table
        and fk.get("referred_columns") == [target_column]
        and (fk.get("options") or {}).get("ondelete", "").upper() == "CASCADE"
        for fk in matching
    ):
        return
    for foreign_key in matching:
        constraint_name = foreign_key.get("name")
        if constraint_name:
            op.drop_constraint(str(constraint_name), table, type_="foreignkey")
    op.create_foreign_key(name, table, target_table, [column], [target_column], ondelete="CASCADE")


def _ensure_postgresql_check(table: str, name: str, expression: str) -> None:
    existing = {constraint["name"] for constraint in sa.inspect(op.get_bind()).get_check_constraints(table)}
    if name not in existing:
        # NOT VALID conserve d'éventuelles données historiques hors bornes tout en
        # protégeant immédiatement toutes les nouvelles écritures.
        op.execute(sa.text(f'ALTER TABLE "{table}" ADD CONSTRAINT "{name}" CHECK ({expression}) NOT VALID'))


def upgrade() -> None:
    connection = op.get_bind()
    # Sur une base vierge, SQLAlchemy crée directement le schéma courant. Sur un
    # ancien volume, create_all ne touche pas les tables et les étapes suivantes
    # effectuent uniquement des ajouts/backfills idempotents.
    Base.metadata.create_all(bind=connection)

    _add_missing_columns(
        "workouts",
        {
            "owner_id": sa.Column("owner_id", sa.String(36), nullable=True),
            "date": sa.Column("date", sa.Date(), nullable=True),
            "type": sa.Column("type", sa.String(80), server_default="Technique", nullable=True),
            "intensity": sa.Column("intensity", sa.Integer(), server_default="6", nullable=True),
            "duration_minutes": sa.Column("duration_minutes", sa.Integer(), server_default="60", nullable=True),
        },
    )
    _add_missing_columns(
        "training_sets",
        {
            "category": sa.Column("category", sa.String(40), server_default="autre", nullable=True),
            "set_count": sa.Column("set_count", sa.Integer(), server_default="1", nullable=True),
            "assistance_kg": sa.Column("assistance_kg", sa.Float(), server_default="0", nullable=True),
        },
    )
    _add_missing_columns(
        "goals",
        {
            "goal_type": sa.Column("goal_type", sa.String(40), server_default="figure", nullable=True),
            "current_value": sa.Column("current_value", sa.Float(), server_default="0", nullable=True),
            "target_value": sa.Column("target_value", sa.Float(), server_default="1", nullable=True),
            "unit": sa.Column("unit", sa.String(40), server_default="autre", nullable=True),
            "priority": sa.Column("priority", sa.String(20), server_default="moyenne", nullable=True),
            "notes": sa.Column("notes", sa.Text(), server_default="", nullable=True),
            "status": sa.Column("status", sa.String(20), server_default="actif", nullable=True),
        },
    )
    _add_missing_columns(
        "import_jobs",
        {
            "owner_id": sa.Column("owner_id", sa.String(36), nullable=True),
            "filename": sa.Column("filename", sa.String(255), server_default="legacy-import.csv", nullable=True),
            "imported_rows": sa.Column("imported_rows", sa.Integer(), server_default="0", nullable=True),
            "rejected_rows": sa.Column("rejected_rows", sa.Integer(), server_default="0", nullable=True),
            "ignored_rows": sa.Column("ignored_rows", sa.Integer(), server_default="0", nullable=True),
            "report": sa.Column("report", sa.Text(), server_default="", nullable=True),
        },
    )

    workout_columns = _columns("workouts")
    statements = [
        "UPDATE workouts SET type = 'Technique' WHERE type IS NULL",
        "UPDATE workouts SET intensity = 6 WHERE intensity IS NULL",
        "UPDATE workouts SET duration_minutes = 60 WHERE duration_minutes IS NULL",
    ]
    if {"user_id", "owner_id"} <= workout_columns:
        statements.append("UPDATE workouts SET owner_id = user_id WHERE owner_id IS NULL")
    if {"performed_on", "date"} <= workout_columns:
        statements.append("UPDATE workouts SET date = performed_on WHERE date IS NULL")
    _execute(statements)

    _execute(
        [
            "UPDATE training_sets SET category = 'autre' WHERE category IS NULL",
            "UPDATE training_sets SET set_count = 1 WHERE set_count IS NULL",
            "UPDATE training_sets SET assistance_kg = 0 WHERE assistance_kg IS NULL",
            "UPDATE goals SET goal_type = 'figure' WHERE goal_type IS NULL",
            "UPDATE goals SET current_value = 0 WHERE current_value IS NULL",
            "UPDATE goals SET target_value = 1 WHERE target_value IS NULL OR target_value <= 0",
            "UPDATE goals SET unit = 'autre' WHERE unit IS NULL",
            "UPDATE goals SET priority = 'moyenne' WHERE priority IS NULL",
            "UPDATE goals SET notes = '' WHERE notes IS NULL",
            "UPDATE goals SET status = 'actif' WHERE status IS NULL",
            "UPDATE import_jobs SET ignored_rows = 0 WHERE ignored_rows IS NULL",
        ]
    )

    import_columns = _columns("import_jobs")
    statements = []
    if {"user_id", "owner_id"} <= import_columns:
        statements.append("UPDATE import_jobs SET owner_id = user_id WHERE owner_id IS NULL")
    if {"file_name", "filename"} <= import_columns:
        statements.append(
            "UPDATE import_jobs SET filename = file_name "
            "WHERE filename IS NULL OR filename = 'legacy-import.csv'"
        )
    if {"rows_accepted", "imported_rows"} <= import_columns:
        statements.append("UPDATE import_jobs SET imported_rows = rows_accepted WHERE imported_rows IS NULL OR imported_rows = 0")
    if {"rows_rejected", "rejected_rows"} <= import_columns:
        statements.append("UPDATE import_jobs SET rejected_rows = rows_rejected WHERE rejected_rows IS NULL OR rejected_rows = 0")
    if {"error_report", "report"} <= import_columns:
        statements.append("UPDATE import_jobs SET report = error_report WHERE report IS NULL OR report = ''")
    statements.extend(
        [
            "UPDATE import_jobs SET filename = 'legacy-import.csv' WHERE filename IS NULL",
            "UPDATE import_jobs SET imported_rows = 0 WHERE imported_rows IS NULL",
            "UPDATE import_jobs SET rejected_rows = 0 WHERE rejected_rows IS NULL",
            "UPDATE import_jobs SET report = '' WHERE report IS NULL",
        ]
    )
    _execute(statements)

    if connection.dialect.name == "postgresql":
        # Si un très ancien enregistrement a perdu son FK mais qu'un utilisateur
        # existe, il est rattaché sans supprimer la donnée avant pose du nouveau FK.
        for table in ("workouts", "goals", "import_jobs"):
            statement = f"UPDATE {table} SET owner_id = (SELECT id FROM users ORDER BY created_at LIMIT 1) WHERE owner_id IS NULL OR NOT EXISTS (SELECT 1 FROM users WHERE users.id = {table}.owner_id)"
            _execute([statement])
        for table, columns in {
            "workouts": ("user_id", "performed_on"),
            "import_jobs": ("user_id", "file_name", "file_hash", "status", "rows_read", "rows_accepted", "rows_rejected"),
        }.items():
            present = _columns(table)
            for column in columns:
                if column in present:
                    op.alter_column(table, column, nullable=True)

    for table, column, column_type in (
        ("workouts", "owner_id", sa.String(36)),
        ("workouts", "date", sa.Date()),
        ("workouts", "type", sa.String(80)),
        ("workouts", "intensity", sa.Integer()),
        ("workouts", "duration_minutes", sa.Integer()),
        ("training_sets", "category", sa.String(40)),
        ("training_sets", "set_count", sa.Integer()),
        ("training_sets", "assistance_kg", sa.Float()),
        ("goals", "goal_type", sa.String(40)),
        ("goals", "current_value", sa.Float()),
        ("goals", "target_value", sa.Float()),
        ("goals", "unit", sa.String(40)),
        ("goals", "priority", sa.String(20)),
        ("goals", "notes", sa.Text()),
        ("goals", "status", sa.String(20)),
        ("import_jobs", "owner_id", sa.String(36)),
        ("import_jobs", "filename", sa.String(255)),
        ("import_jobs", "imported_rows", sa.Integer()),
        ("import_jobs", "rejected_rows", sa.Integer()),
        ("import_jobs", "ignored_rows", sa.Integer()),
        ("import_jobs", "report", sa.Text()),
    ):
        _ensure_not_null(table, column, column_type)

    _ensure_index("workouts", "ix_workouts_owner_id", ["owner_id"])
    _ensure_index("workouts", "ix_workouts_owner_date", ["owner_id", "date"])
    _ensure_index("goals", "ix_goals_owner_id", ["owner_id"])
    _ensure_index("goals", "ix_goals_owner_status", ["owner_id", "status"])
    _ensure_index("import_jobs", "ix_import_jobs_owner_id", ["owner_id"])
    _ensure_index("import_jobs", "ix_import_jobs_owner_created", ["owner_id", "created_at"])

    if connection.dialect.name == "postgresql":
        _ensure_cascade_fk("workouts", "owner_id", "users", "id", "fk_workouts_owner_id_users")
        _ensure_cascade_fk("goals", "owner_id", "users", "id", "fk_goals_owner_id_users")
        _ensure_cascade_fk("import_jobs", "owner_id", "users", "id", "fk_import_jobs_owner_id_users")
        _ensure_cascade_fk("training_sets", "workout_id", "workouts", "id", "fk_training_sets_workout_id")
        for table, name, expression in (
            ("workouts", "ck_workouts_intensity", "intensity BETWEEN 1 AND 10"),
            ("workouts", "ck_workouts_duration_minutes", "duration_minutes BETWEEN 1 AND 1440"),
            ("training_sets", "ck_training_sets_set_count", "set_count BETWEEN 1 AND 50"),
            ("training_sets", "ck_training_sets_reps", "reps BETWEEN 0 AND 1000"),
            ("training_sets", "ck_training_sets_load_kg", "load_kg BETWEEN 0 AND 1000"),
            ("training_sets", "ck_training_sets_duration_seconds", "duration_seconds BETWEEN 0 AND 86400"),
            ("training_sets", "ck_training_sets_difficulty", "difficulty BETWEEN 1 AND 10"),
            ("training_sets", "ck_training_sets_assistance_kg", "assistance_kg BETWEEN 0 AND 1000"),
            ("goals", "ck_goals_current_value", "current_value >= 0"),
            ("goals", "ck_goals_target_value", "target_value > 0"),
            ("goals", "ck_goals_priority", "priority IN ('basse', 'moyenne', 'haute')"),
            ("goals", "ck_goals_status", "status IN ('actif', 'termine', 'archive')"),
            ("import_jobs", "ck_import_jobs_imported_rows", "imported_rows >= 0"),
            ("import_jobs", "ck_import_jobs_rejected_rows", "rejected_rows >= 0"),
            ("import_jobs", "ck_import_jobs_ignored_rows", "ignored_rows >= 0"),
        ):
            _ensure_postgresql_check(table, name, expression)


def downgrade() -> None:
    # Cette première révision absorbe plusieurs schémas historiques. Un downgrade
    # automatique supprimerait potentiellement des données : il est volontairement
    # non destructif. Une restauration doit utiliser un backup PostgreSQL.
    pass
