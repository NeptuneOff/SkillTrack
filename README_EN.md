# SkillTrack Calisthenics

SkillTrack is a full-stack training log application focused on calisthenics. It provides authentication, workout tracking, skill progression, CSV import, JSON/CSV export, statistics, tests, Docker, CI and RNCP evidence documentation.

## Quick start

```bash
git clone https://github.com/NeptuneOff/SkillTrack.git
cd SkillTrack
cp .env.example .env
docker compose up --build
```

Available services:

- Frontend: http://localhost:5173
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Healthcheck: http://localhost:8000/health
- PostgreSQL: localhost:5432
- MailHog: http://localhost:8025

Demo account:

- Email: demo@skilltrack.local
- Password: DemoPassword123!

## Project goal

The goal is to replace a manual and fragmented training log with a structured web application. The application stores sessions, exercises, sets and progression records. It helps users understand their training history and export their own data.

## Technical stack

- Backend: Python, FastAPI, SQLAlchemy, Pydantic, PostgreSQL
- Frontend: React, TypeScript, Vite
- Tests: pytest, coverage, Vitest
- Quality: Ruff, mypy, ESLint, Prettier
- Deployment: Docker, Docker Compose, GitHub Actions
- External service for integration proof: MailHog SMTP test service

## Main commands

```bash
# Start the stack
docker compose up --build

# Backend tests
docker compose run --rm backend pytest -q --cov=app --cov-report=term-missing

# Backend lint
docker compose run --rm backend ruff check app tests

# Frontend tests
docker compose run --rm frontend npm test -- --run

# Linux/macOS reproducible setup
./scripts/setup.sh

# Windows reproducible setup
./scripts/setup.ps1
```

## API overview

- `POST /auth/register` creates a user.
- `POST /auth/login` returns a JWT access token.
- `GET /workouts` lists the authenticated user's workouts.
- `POST /workouts` creates a workout.
- `GET /stats/weekly-volume` returns weekly volume aggregates.
- `POST /imports/workouts` imports a CSV file.
- `GET /exports/workouts.csv` exports user-owned data as CSV.
- `GET /exports/workouts.json` exports user-owned data as JSON.

## Evidence mindset

The repository is designed to produce verifiable evidence: source code, tests, CI reports, Docker scripts, architecture decisions, risk register, RGPD register, RGAA checklist, RSE metrics and ITIL integration procedure. Each important claim in the RNCP portfolio must be linked to a real file, a command output, a date and a commit.
