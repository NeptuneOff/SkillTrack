# SkillTrack — Calisthenics Progress Tracker

SkillTrack is a full-stack web application for tracking calisthenics training sessions, exercises, sets and skill progression. It is designed as a demonstrable technical project for a level-6 application development portfolio.

## Delivered features

- JWT authentication.
- Demo user seeded at startup.
- Dashboard with global and weekly metrics.
- Complete workout CRUD.
- Exercise/set tracking with automatic volume calculation.
- Goal tracking and skill progress.
- CSV import with validation report.
- CSV and JSON export.
- User profile with data export and deletion workflow.
- Swagger API documentation.
- Docker Compose stack: React frontend, FastAPI backend, PostgreSQL and MailHog.
- Backend and frontend tests.
- Project documentation in `/docs`.

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

URLs:

- Frontend: http://localhost:5173
- Swagger: http://localhost:8000/docs
- MailHog: http://localhost:8025

Demo account:

- Email: `demo@skilltrack.dev`
- Password: `DemoPassword123!`

## Jury demonstration

Start the stack, sign in, inspect the real dashboard data, create/edit/delete a workout, add and remove an exercise, manage a measurable goal, import the sample CSV and inspect its report, download the authenticated CSV/JSON exports, then show Swagger, tests and the RNCP evidence matrix. Known limitations are recorded in `docs/rncp/CONTROLE_FINAL.md` and `docs/rncp/MATRICE_COMPETENCES_RNCP.md`.

The backend intentionally pins `bcrypt==4.0.1` for Passlib compatibility. The frontend Docker image uses Node 22.
