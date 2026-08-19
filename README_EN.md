# SkillTrack — Calisthenics Progress Tracker

SkillTrack is a full-stack web application for recording workouts, measurable goals and calisthenics progress. It also serves as a technical demonstrator and evidence portfolio for the French level-6 **RNCP 36463 — Concepteur développeur d'applications numériques** qualification.

## Delivered scope

- JWT authentication and a local demo account;
- PostgreSQL-backed dashboard metrics;
- workout and exercise create/read/update/delete flows;
- measurable goal create/edit/complete/reopen/delete flows;
- UTF-8 CSV import (2 MB limit) with row-level error report and history;
- authenticated CSV and structured JSON exports;
- profile, portability and account erasure;
- a non-blocking goal-completion message delivered to MailHog in development;
- Swagger, Alembic migrations, locked Python/Node dependencies, Docker Compose, CI, backend/frontend/E2E tests and a performance script;
- a traceable RNCP documentation set under `docs/`.

Out of scope: public sign-up/password recovery, medical coaching, native mobile applications, production cloud operations and asynchronous high-volume import. The default account and secrets are for local development only.

## Quick start

Requirements: Git, a recent Docker Engine/Desktop with Compose, and free ports 5173, 8000, 5432 and 8025. Python 3 is also required by the complete verification script, but not to use the Docker stack itself.

```bash
git clone https://github.com/NeptuneOff/SkillTrack.git
cd SkillTrack
cp .env.example .env
docker compose up --build -d
docker compose ps
```

On Windows PowerShell, use `Copy-Item .env.example .env` or run `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1`. On Linux/macOS, `./scripts/setup.sh` provides the equivalent setup.

| Service | URL |
|---|---|
| Web app | http://localhost:5173 |
| Swagger API | http://localhost:8000/docs |
| API health | http://localhost:8000/health |
| MailHog development UI | http://localhost:8025 |

Demo credentials: `demo@skilltrack.dev` / `DemoPassword123!`. Never expose them on a public deployment.

## Verification

Run the complete local quality gate:

```bash
./scripts/verify.sh
```

or on PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

It covers backend lint, typing and tests; frontend tests, lint and build; the Compose Playwright profile; the live smoke test; and the benchmark unless skipped. The valid release evidence is the output and CI result attached to the exact commit being presented.

Latest complete local gate on 2026-08-19: **PASS** — development/production builds and health, Alembic `20260819_03`, Ruff/mypy, backend 20/20 with no warning and 92.36% application coverage, frontend 10/10 plus build, Chromium Playwright 2/2, smoke 9/9 with cleanup, and performance 200/200 (p95 128.05 ms against a 1,000 ms threshold). Versionable evidence is indexed in [`docs/INDEX.md`](docs/INDEX.md); attach the run to the final commit hash and confirm it in CI.

## Architecture

```text
React/Vite browser client
        │ REST JSON/CSV + JWT
        ▼
FastAPI ── SQLAlchemy/psycopg ── PostgreSQL 16
        └── development SMTP ── MailHog
```

The backend is a compact MVP monolith with a repository port separating business services from the SQLAlchemy/PostgreSQL adapter. Versioned Alembic migrations upgrade the existing demo volume. A separate multi-stage `docker-compose.prod.yml` provides a hardened runtime simulation, validated against an isolated fresh database but not operated as a public production service.

## CSV import

The required headers are `date,title,exercise`. Download the example from the Import/Export page or use `samples/import_workouts.csv`. The complete field mapping and interoperability tests are documented in [`docs/annexes/J_import_export.md`](docs/annexes/J_import_export.md).

## Safe operations

Create a database backup with `scripts/backup.sh`, or on Windows with `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\backup.ps1`. Stop the stack with `docker compose down`. Do not add `-v`, as it removes the PostgreSQL volume. See [`docs/annexes/K_ITIL_deploiement.md`](docs/annexes/K_ITIL_deploiement.md) for the verified restore procedure and Go/No-Go checklist.

## Jury demonstration

Show the healthy Compose stack, sign in, inspect database-backed metrics, complete the workout and goal life cycles, display the goal-completion message in MailHog, import a CSV containing an invalid row, download both exports, explain ownership filtering and GDPR rights, then show Swagger, tests, CI and the [36-competency evidence matrix](docs/rncp/MATRICE_COMPETENCES_RNCP.md). A detailed French [user guide](docs/GUIDE_UTILISATEUR.md) is also included.

The repository is honest about evidence boundaries: user interviews, teamwork, company-process evidence, external reviews and acceptance signatures must come from real people and are never generated as placeholders.

The French [evidence portfolio index](docs/INDEX.md) links specifications, architecture, data model, security, testing, operations and the official competency matrix.

## Before production

Use strong managed secrets, HTTPS, a hardened JWT/session policy, rate limiting, maintained lockfiles plus Python SBOM/audits, a tested migration/rollback policy, monitored backups/logs, a real SMTP relay, a published privacy notice, human accessibility acceptance and representative load tests. The frontend images deliberately use Node 22. The backend uses direct `bcrypt==5.0.0`; passwords beyond 72 UTF-8 bytes are explicitly rejected rather than silently truncated.
