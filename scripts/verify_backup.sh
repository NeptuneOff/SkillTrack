#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || ! -f "$1" ]]; then
  echo "Usage: $0 artifacts/backups/skilltrack-YYYYMMDD-HHMMSS.dump" >&2
  exit 1
fi

cd "$(dirname "$0")/.."
backup_path="$1"
restore_db="skilltrack_restore_$(openssl rand -hex 5)"
container_path="/tmp/$restore_db.dump"

docker compose cp "$backup_path" "db:$container_path"
cleanup() {
  docker compose exec -T db sh -c 'dropdb -U "$POSTGRES_USER" --if-exists "$1"' sh "$restore_db" >/dev/null 2>&1 || true
  docker compose exec -T db rm -f -- "$container_path" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker compose exec -T db sh -c 'createdb -U "$POSTGRES_USER" "$1"' sh "$restore_db"
docker compose exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d "$1" --no-owner --no-privileges "$2"' sh "$restore_db" "$container_path"
docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$1" --set ON_ERROR_STOP=1 -At -c "SELECT '\''users='\'' || (SELECT count(*) FROM users) || '\'', workouts='\'' || (SELECT count(*) FROM workouts) || '\'', goals='\'' || (SELECT count(*) FROM goals) || '\'', imports='\'' || (SELECT count(*) FROM import_jobs);"' sh "$restore_db"
echo "Backup restored successfully in an isolated temporary database."
