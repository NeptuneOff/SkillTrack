#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

skip_performance=false
skip_e2e=false
skip_production_build=false
for argument in "$@"; do
  case "$argument" in
    --skip-performance) skip_performance=true ;;
    --skip-e2e) skip_e2e=true ;;
    --skip-production-build) skip_production_build=true ;;
    *) echo "Unknown option: $argument" >&2; exit 2 ;;
  esac
done

command -v docker >/dev/null 2>&1 || { echo "Docker is required." >&2; exit 1; }
if command -v python3 >/dev/null 2>&1; then
  python_command=python3
elif command -v python >/dev/null 2>&1; then
  python_command=python
else
  echo "Python 3 is required." >&2
  exit 1
fi
if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created local .env from .env.example."
fi
mkdir -p artifacts/validation artifacts/performance

docker compose config --quiet
docker compose --file docker-compose.prod.yml config --quiet
if [[ "$skip_production_build" != true ]]; then
  docker compose --file docker-compose.prod.yml build backend frontend
fi
docker compose up --build --detach --wait --wait-timeout 180 --remove-orphans
docker compose exec -T db sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" --set ON_ERROR_STOP=1 -Atc "SELECT current_database(), version();"'
docker compose exec -T backend alembic -c app/alembic.ini current --check-heads
docker compose exec -T backend ruff check app tests
docker compose exec -T backend mypy app
docker compose exec -T backend pytest -q \
  --cov=app --cov-fail-under=90 --cov-report=term-missing \
  --cov-report=xml:/tmp/backend-coverage.xml --junitxml=/tmp/backend-junit.xml
docker compose cp backend:/tmp/backend-coverage.xml artifacts/validation/backend-coverage.xml
docker compose cp backend:/tmp/backend-junit.xml artifacts/validation/backend-junit.xml
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm test -- --run \
  --reporter=default --reporter=junit --outputFile.junit=/tmp/frontend-junit.xml
docker compose cp frontend:/tmp/frontend-junit.xml artifacts/validation/frontend-junit.xml
docker compose exec -T frontend npm run build
if [[ "$skip_e2e" != true ]]; then
  docker compose --profile test run --rm e2e
fi
"$python_command" scripts/smoke_test.py \
  --mailhog-url http://localhost:8025 \
  --output artifacts/validation/smoke.json

if [[ "$skip_performance" != true ]]; then
  "$python_command" scripts/performance_test.py --users 20 --requests 200 --output artifacts/performance/latest.json
fi

echo "Full verification passed. Reports: artifacts/validation"
