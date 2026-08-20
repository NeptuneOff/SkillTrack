# K — Intégrabilité ITIL et runbook d'exploitation

## 1. Objet et responsabilités

Cette procédure contrôle l'intégration d'une release SkillTrack dans l'environnement de test local. Elle s'inspire de la gestion de changement ITIL ; elle ne prétend pas constituer une certification ITIL.

| Rôle | Responsabilité | Titulaire |
|---|---|---|
| Demandeur/changement | décrit périmètre, risques et retour arrière | Karl |
| Réalisateur | construit, teste, sauvegarde et déploie | Karl |
| Valideur technique | revue du Go/No-Go | pair à identifier |
| Valideur fonctionnel | recette et acceptation | utilisateur/commanditaire à identifier |

## 2. Préconditions

- commit et branche identifiés ; worktree propre ;
- `.env` local créé depuis `.env.example`, secrets remplacés si exposition réseau ;
- Docker/Compose disponibles et ports libres ;
- espace disque suffisant ;
- sauvegarde datée pour toute base non jetable ;
- plan de rollback et personne décisionnaire connus ;
- révision Alembic courante et compatibilité du volume identifiées.

## 3. Procédure d'intégration

```powershell
git status --short
docker compose config
docker compose up --build --detach --wait --wait-timeout 180
docker compose ps
docker compose exec -T backend alembic -c app/alembic.ini current --check-heads
docker compose exec -T backend ruff check app tests
docker compose exec -T backend mypy app
docker compose exec -T backend pytest -q --cov=app --cov-report=term-missing
docker compose exec -T frontend npm test -- --run
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build
docker compose --profile test run --rm e2e
python scripts/smoke_test.py
```

Sous Windows, lancer le contrôle même si la stratégie d'exécution locale bloque les scripts :

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
```

Sous Linux/macOS, `./scripts/verify.sh` fournit l'équivalent.

## 4. Go/No-Go

Go seulement si : services `healthy`, tests/lint/types/build et E2E verts, smoke réussi, migrations Alembic testées, export parsable, recette critique sans anomalie, sauvegarde vérifiée et rollback applicable. Toute fuite inter-utilisateur, perte de données, échec auth/navigation ou migration irréversible impose **No-Go**.

## 5. Sauvegarde et restauration sûre

Sous Windows, utiliser `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\backup.ps1` ; sous Linux/macOS, `./scripts/backup.sh`. Les dumps contiennent des données personnelles : ils restent hors Git, avec droits restreints, durée de conservation définie et suppression contrôlée.

Preuve du 19/08/2026 : sauvegarde locale réussie (empreinte enregistrée sous forme abrégée `F8E80A…6167C`), restauration dans une base temporaire isolée puis contrôle `users=1`, `workouts=5`, `goals=5`, `imports=7`. La base temporaire a ensuite été supprimée. Journal sans dump : `artifacts/operations/2026-08-19-backup-restore.md`.

## 6. Rollback

1. déclarer le No-Go et arrêter les écritures ;
2. conserver logs et identifiant de release ;
3. arrêter les services applicatifs sans supprimer les volumes ;
4. revenir au tag/commit stable sur une branche de restauration ;
5. reconstruire les images ;
6. si le schéma a changé, restaurer le dump dans une base isolée puis basculer après contrôle ;
7. exécuter healthcheck, smoke et comptages d'intégrité ;
8. documenter incident, décision et temps de rétablissement.

Ne jamais utiliser `docker compose down -v` comme rollback : l'option `-v` supprime le volume PostgreSQL. Ne jamais écraser une base avant d'avoir testé la sauvegarde dans une base distincte.

## 7. Diagnostic

```powershell
docker compose ps
docker compose logs --tail=200 backend
docker compose logs --tail=200 frontend
docker compose logs --tail=200 db
Invoke-RestMethod http://localhost:8000/health
```

Vérifier dans l'ordre : configuration effective (`docker compose config` sans publier les secrets), santé BDD, startup API, CORS/URL frontend, code HTTP et console navigateur.

## 8. Journal de changement

| Champ | Valeur à renseigner |
|---|---|
| Release/commit | |
| Périmètre | |
| Risques et sauvegarde | |
| Début/fin | |
| Résultats de contrôles | |
| Incidents/contournements | |
| Décision et valideur | |

Le test technique de restauration est une preuve solide ; la décision de mise en exploitation par une partie habilitée reste une validation externe requise.

## 9. Simulation production

`docker-compose.prod.yml` construit les cibles multi-stage sans montage du code ni `--reload`, exige les variables PostgreSQL/secret, rend le backend en lecture seule avec `/tmp` temporaire et sert le frontend via Nginx non privilégié. Valider sa configuration sans démarrer avec :

```powershell
docker compose --file docker-compose.prod.yml config --quiet
```

Preuve exécutée le 19/08/2026 dans un projet/volume temporaires : images production reconstruites, base PostgreSQL vierge migrée, `/healthz` frontend et proxy same-origin `/api/health` à HTTP 200, connexion JWT réussie, services sains, puis volume temporaire supprimé. Journal et commandes : `artifacts/operations/2026-08-19-production-smoke.md`.

Cette simulation durcie ne fournit ni DNS/TLS, ni coffre de secrets, ni sauvegarde planifiée, ni supervision. Elle n'est donc pas assimilée à un hébergement de production réel.
