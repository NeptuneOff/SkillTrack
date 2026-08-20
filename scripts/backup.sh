#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
destination="${1:-artifacts/backups}"
mkdir -p "$destination"
backup_name="skilltrack-$(date -u +%Y%m%d-%H%M%S).dump"
container_path="/tmp/$backup_name"
host_path="$destination/$backup_name"

docker compose exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom --file="$1"' sh "$container_path"
trap 'docker compose exec -T db rm -f -- "$container_path" >/dev/null 2>&1 || true' EXIT
docker compose cp "db:$container_path" "$host_path"

echo "Backup created: $host_path"
sha256sum "$host_path"
