# SkillTrack Calisthenics

SkillTrack est une application web de suivi d'entraînement orientée calisthénie. Le projet couvre un MVP complet : authentification, gestion des séances, séries, progression sur les skills, import CSV, export JSON/CSV, statistiques, sécurité, tests, Docker, CI et documentation de preuves RNCP 36463.

## Lancer le projet rapidement

### Prérequis

- Docker Desktop ou Docker Engine récent
- Docker Compose
- Git

### Installation

```bash
git clone https://github.com/NeptuneOff/SkillTrack.git
cd SkillTrack
cp .env.example .env
docker compose up --build
```

Services disponibles :

- Frontend : http://localhost:5173
- API : http://localhost:8000
- Swagger : http://localhost:8000/docs
- Healthcheck : http://localhost:8000/health
- Base PostgreSQL : localhost:5432
- MailHog SMTP de test : http://localhost:8025

Compte de démonstration créé par le seed :

- Email : demo@skilltrack.local
- Mot de passe : DemoPassword123!

## Commandes utiles

```bash
# Lancer tout le projet
docker compose up --build

# Exécuter les tests backend
docker compose run --rm backend pytest -q --cov=app --cov-report=term-missing

# Lint backend
docker compose run --rm backend ruff check app tests

# Tests frontend
docker compose run --rm frontend npm test -- --run

# Installation reproductible + smoke test Linux/macOS
./scripts/setup.sh

# Installation reproductible + smoke test Windows PowerShell
./scripts/setup.ps1
```

## Architecture

```text
Frontend React/TypeScript
        ↓ HTTP JSON
Backend FastAPI
        ↓ services métier
Repositories SQLAlchemy
        ↓ migrations / contraintes
PostgreSQL
```

Composants secondaires :

- MailHog pour simuler l'intégration d'un service externe de messagerie.
- Docker Compose pour l'environnement reproductible.
- Scripts `setup.sh` et `setup.ps1` pour automatiser l'installation et les tests de fumée.
- GitHub Actions pour lint, tests et build.

## Périmètre fonctionnel MVP

- Création de compte et connexion JWT.
- CRUD des séances d'entraînement.
- Ajout d'exercices et séries.
- Calculs de volume et statistiques hebdomadaires.
- Suivi des skills de calisthénie.
- Import CSV avec prévisualisation, rapport d'erreurs, idempotence et `ImportJob` asynchrone si le fichier dépasse le seuil.
- Export CSV et JSON des données appartenant à l'utilisateur.
- Tests unitaires et d'intégration.
- Contrôles de sécurité : hash de mot de passe, filtrage par utilisateur, contraintes BDD, validation Pydantic, CORS borné.

## Structure

```text
backend/              API FastAPI, services, repositories, modèles, tests
frontend/             Application React/TypeScript
scripts/              setup, smoke test, reset
infra/                SQL init et scripts utiles
docs/                 preuves RNCP, ADR, RGPD, RGAA, RSE, ITIL, qualité
docs/evidence/        modèles de preuves à compléter pendant le projet
.github/workflows/    CI
```

## Preuves RNCP préparées

Le dossier `docs/` contient un système de preuves aligné avec les 36 compétences :

- `docs/RNCP_COVERAGE.md` : correspondance compétences → fichiers/preuves.
- `docs/proof_matrix.csv` : matrice exploitable dans le dossier.
- `docs/quality/PAQ.md` : plan assurance qualité.
- `docs/security/RISK_REGISTER.md` : registre des risques.
- `docs/privacy/RGPD_REGISTER.md` : registre RGPD.
- `docs/accessibility/RGAA_AUDIT.md` : audit RGAA à exécuter.
- `docs/sustainability/RSE_METRICS.md` : métriques RSE.
- `docs/itil/INTEGRATION_PROCEDURE.md` : procédure d'intégrabilité et rollback.
- `docs/adr/` : décisions d'architecture.
- `docs/import_export/` : mapping CSV/JSON et exemples.

Chaque preuve doit être datée, versionnée, liée à un commit et accompagnée d'un résultat réel avant la version finale.

## Décisions techniques principales

- FastAPI pour l'API Python typée et documentée automatiquement.
- PostgreSQL pour les contraintes, transactions, index et intégrité.
- SQLAlchemy 2.0 pour isoler le stockage derrière des repositories.
- React + TypeScript pour une interface maintenable.
- Docker Compose pour une installation reproductible.
- MailHog comme service externe local de messagerie.
- Ruff, mypy, pytest, Vitest et GitHub Actions pour qualité et non-régression.

## Sécurité et confidentialité

- Les mots de passe sont hashés avec bcrypt.
- Les routes métier nécessitent un JWT valide.
- Chaque requête métier filtre par `user_id`.
- Les imports sont validés avant insertion.
- Les transactions évitent les insertions partielles incohérentes.
- Les exports ne contiennent que les données du propriétaire authentifié.
- Le registre RGPD précise les finalités, durées et droits.

## Licence

Projet pédagogique RNCP — usage de démonstration.
