#!/usr/bin/env bash
set -euo pipefail
docker compose down -v
docker compose up --build -d
python scripts/smoke_test.py
