# SkillTrack — suivi de progression en calisthénie

SkillTrack est une application web complète de suivi d'entraînement : séances et exercices, objectifs mesurables, statistiques, import CSV, exports CSV/JSON et droits RGPD. Elle constitue un démonstrateur technique et un portefeuille de preuves pour le titre **Concepteur développeur d'applications numériques, RNCP 36463, niveau 6**.

## Ce qui est livré

- authentification JWT et compte de démonstration ;
- dashboard calculé depuis PostgreSQL ;
- création, consultation, modification et suppression des séances ;
- ajout/suppression d'exercices avec séries, répétitions, charge, assistance et maintien ;
- objectifs créables, modifiables, terminables, réouvrables et supprimables ;
- import CSV UTF-8 limité à 2 Mo, rapport d'erreurs et historique ;
- exports CSV et JSON authentifiés ;
- profil, portabilité et effacement du compte ;
- notification de fin d'objectif visible dans MailHog en développement ;
- API Swagger, migrations Alembic, dépendances Python/Node verrouillées, stack Docker Compose, CI, tests backend/frontend/E2E et benchmark ;
- documentation RNCP structurée dans `docs/`.

Limites assumées : pas d'inscription publique/récupération de mot de passe, pas de déploiement cloud de production, pas de coaching médical, import synchrone uniquement. La configuration par défaut et le compte démo sont réservés au développement local.

## Démarrage en cinq minutes

### Prérequis

- Git ;
- Docker Desktop ou Docker Engine avec `docker compose` ;
- ports 5173, 8000, 5432 et 8025 disponibles ;
- Python 3 pour la vérification complète (smoke et benchmark) ; non requis pour simplement utiliser la stack Docker.

### Windows PowerShell

```powershell
git clone https://github.com/NeptuneOff/SkillTrack.git
Set-Location SkillTrack
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
```

Ou utiliser :

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1
```

### Linux/macOS

```bash
git clone https://github.com/NeptuneOff/SkillTrack.git
cd SkillTrack
cp .env.example .env
docker compose up --build -d
docker compose ps
```

Ou utiliser `./scripts/setup.sh`.

Attendre que `db` et `backend` soient sains, puis ouvrir :

| Service | Adresse |
|---|---|
| Application | http://localhost:5173 |
| API Swagger | http://localhost:8000/docs |
| Santé API | http://localhost:8000/health |
| MailHog (développement) | http://localhost:8025 |

Compte local de démonstration :

- e-mail : `demo@skilltrack.dev`
- mot de passe : `DemoPassword123!`

Ne jamais exposer ce compte ou les secrets de `.env.example` sur Internet.

## Vérification complète

Le contrôle automatisé recommandé est :

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

ou :

```bash
./scripts/verify.sh
```

Contrôles principaux exécutés par le script (celui-ci valide aussi les modèles Compose, les migrations, le build production et archive des rapports) :

```powershell
docker compose exec -T backend ruff check app tests
docker compose exec -T backend mypy app
docker compose exec -T backend pytest -q --cov=app --cov-report=term-missing --cov-fail-under=90
docker compose exec -T frontend npm test -- --run
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build
docker compose --profile test run --rm e2e
python scripts/smoke_test.py
python scripts/performance_test.py
```

Le script exécute aussi le parcours Playwright via le profil Compose `test`. La preuve valable pour une release est la sortie associée au commit présenté, pas un ancien nombre de tests recopié dans ce fichier.

Dernier contrôle complet local du 20/08/2026 sur l'état final : **PASS** — builds/health dev et production, Alembic `20260820_04`, Ruff/mypy, backend 21/21 sans warning à 92,33 %, frontend 10/10 + build, Playwright Chromium 2/2, smoke 9/9 avec nettoyage et benchmark 200/200 (p95 124,74 ms pour un seuil de 1 000 ms). Les preuves versionnables sont regroupées dans [`docs/INDEX.md`](docs/INDEX.md) ; ce résultat doit être rattaché au hash final et confirmé par la CI.

## Format CSV

Colonnes minimales : `date,title,exercise`. Utiliser le modèle de l'écran Import/Export ou `samples/import_workouts.csv`.

```csv
date,title,type,intensity,duration_minutes,exercise,reps,load_kg,duration_seconds,difficulty,notes
2026-08-19,Push technique,Push,7,60,Tuck planche,0,0,20,7,Bon contrôle scapulaire
```

Le mapping complet, les valeurs par défaut, erreurs et contrats d'export sont documentés dans [`docs/annexes/J_import_export.md`](docs/annexes/J_import_export.md).

## Architecture

```text
Navigateur React/Vite
        │ REST JSON/CSV + JWT
        ▼
API FastAPI ── SQLAlchemy/psycopg ── PostgreSQL 16
        └── SMTP de développement ── MailHog
```

Compose fournit les services, healthchecks et un profil E2E. Le backend reste un monolithe compact adapté au MVP, avec un port repository séparant les services métier de l'adaptateur SQLAlchemy/PostgreSQL. Alembic applique les migrations canoniques et conserve l'ancien volume. `docker-compose.prod.yml` simule un runtime multi-stage durci, validé sur une base temporaire vierge, sans être un hébergement de production. Voir [`docs/annexes/D_architecture.md`](docs/annexes/D_architecture.md) et le [journal de smoke production](artifacts/operations/2026-08-19-production-smoke.md).

## Sauvegarde et arrêt

Créer une sauvegarde avant toute opération sur une base utile :

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\backup.ps1
```

```bash
./scripts/backup.sh
```

Arrêt sans effacer les données :

```powershell
docker compose down
```

N'utilisez pas `docker compose down -v` : cette option supprime le volume PostgreSQL. Le runbook et le test de restauration sont dans [`docs/annexes/K_ITIL_deploiement.md`](docs/annexes/K_ITIL_deploiement.md).

## Démonstration jury (12 à 15 minutes)

1. Montrer `docker compose ps`, le healthcheck et le commit présenté.
2. Se connecter puis expliquer les métriques issues de PostgreSQL.
3. Créer une séance avec deux exercices, en retirer un, enregistrer, modifier et supprimer.
4. Créer un objectif mesurable, le modifier et le terminer ; montrer la notification dans MailHog, puis le rouvrir et le supprimer.
5. Importer le CSV exemple avec une ligne erronée et commenter le rapport.
6. Télécharger CSV/JSON et montrer l'isolation par utilisateur.
7. Présenter le profil, la portabilité et l'effacement sans supprimer le compte avant la fin.
8. Ouvrir Swagger, lancer la vérification et montrer la CI du même commit.
9. Relier les preuves aux 36 compétences via la matrice.
10. Annoncer honnêtement les limites et les validations externes restantes.

## Dossier RNCP

- [Index du portefeuille de preuves](docs/INDEX.md)
- [Matrice officielle 10/13/8/5](docs/rncp/MATRICE_COMPETENCES_RNCP.md)
- [Contrôle final](docs/rncp/CONTROLE_FINAL.md)
- [Guide utilisateur](docs/GUIDE_UTILISATEUR.md)
- [Cahier des charges](docs/annexes/A_cahier_des_charges.md)
- [Architecture et ADR](docs/annexes/D_architecture.md)
- [MCD/MPD et dictionnaire](docs/annexes/E_mcd_mpd.md)
- [Sécurité et risques](docs/annexes/F_securite.md)
- [Tests, recette et PV](docs/annexes/I_tests_recette.md)
- [ITIL et exploitation](docs/annexes/K_ITIL_deploiement.md)
- [Processus/AS-IS/TO-BE/flux](docs/annexes/P_processus_et_flux.md)

La documentation prépare les livrables, mais ne fabrique pas les entretiens, heures, décisions collectives, validations d'entreprise ou signatures. Ces pièces doivent provenir de situations réelles.

## Production

Avant exposition publique : secrets robustes, HTTPS/proxy, politique JWT, rate limiting, maintien/audit des lockfiles et SBOM Python, stratégie de migrations/rollback, sauvegardes supervisées, logs/alertes, relais SMTP réel, politique RGPD publiée, recette accessibilité humaine et tests de charge représentatifs.

Compatibilité imposée par le projet : Node 22 dans les images frontend. Le backend utilise directement `bcrypt==5.0.0`; les mots de passe dépassant 72 octets UTF-8 sont rejetés explicitement au lieu d'être tronqués silencieusement.
