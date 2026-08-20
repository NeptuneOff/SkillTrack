#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required and must be available in PATH." >&2
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker is installed but its engine is not responding." >&2
  exit 1
fi

production=false
if [[ "${1:-}" == "--production" ]]; then
  production=true
elif [[ $# -gt 0 ]]; then
  echo "Usage: $0 [--production]" >&2
  exit 2
fi

if [[ ! -f .env ]]; then
  if [[ "$production" == true ]]; then
    echo "Create a production-specific .env file before using --production." >&2
    exit 1
  fi
  cp .env.example .env
  echo "Created .env from .env.example. Change SECRET_KEY before public deployment."
fi

if [[ "$production" == true ]]; then
  secret_value="$(sed -n 's/^SECRET_KEY=//p' .env | tail -n 1)"
  database_password="$(sed -n 's/^POSTGRES_PASSWORD=//p' .env | tail -n 1)"
  if [[ ${#secret_value} -lt 32 || "$secret_value" == "change-this-secret-for-local-demo" ]]; then
    echo "SECRET_KEY must be a dedicated random value of at least 32 characters in production." >&2
    exit 1
  fi
  if [[ -z "$database_password" || "$database_password" == "skilltrack" ]]; then
    echo "POSTGRES_PASSWORD must be replaced by a dedicated production secret." >&2
    exit 1
  fi
fi

compose_args=(compose)
if [[ "$production" == true ]]; then
  compose_args+=(--file docker-compose.prod.yml)
fi

docker "${compose_args[@]}" config --quiet
docker "${compose_args[@]}" up --build --detach --wait --wait-timeout "${SKILLTRACK_WAIT_TIMEOUT:-180}" --remove-orphans
docker "${compose_args[@]}" ps

echo "SkillTrack is ready: UI http://localhost:5173"
if [[ "$production" != true ]]; then
  echo "API http://localhost:8000/docs - demo emails http://localhost:8025"
fi
