# Contrôle final avant démonstration jury

Ce document est une grille de recette. Une case ne doit être cochée qu'après exécution sur la machine de présentation.

| # | Critère | Preuve attendue | État dépôt |
|---|---|---|---|
| 1 | Utilisable sans explication | Titres, aides, compte démo, README | À valider en test utilisateur |
| 2 | Toutes les pages ont une interface | Dashboard, séances, objectifs, import/export, profil | Couvert |
| 3 | Boutons fonctionnels/désactivés | Parcours manuel complet | À valider avec Compose |
| 4 | Formulaires guidés/validés | Labels HTML + Pydantic | Couvert pour login/séances/import ; objectifs à approfondir |
| 5 | Dashboard avec vraies données | PostgreSQL + données démo | Couvert |
| 6 | CRUD séances | `/workouts` + interface + tests | Couvert |
| 7 | Ajout/suppression exercices | Formulaire séance | Couvert |
| 8 | CRUD/statut objectifs | `/goals` + `GoalsPage.jsx` | Couvert |
| 9 | Import et rapport | `/imports/csv`, rapport immédiat, historique API | Couvert ; affichage de l'historique UI optionnel à ajouter |
| 10 | Exports CSV/JSON | téléchargement authentifié | Couvert |
| 11 | JWT | login + dépendance Bearer | Couvert |
| 12 | Filtrage utilisateur | filtres `owner_id` | Couvert ; test multi-utilisateur à ajouter |
| 13 | PostgreSQL | URL Compose psycopg | Couvert en environnement Docker |
| 14 | Docker Compose | healthchecks/4 services | À exécuter sur machine jury |
| 15 | README autonome | démarrage, URLs, tests | Couvert, scénario à maintenir |
| 16 | Tests fonctions principales | backend + frontend | Partiel : frontend encore insuffisant |
| 17 | Documentation RNCP | `docs/annexes`, `docs/rncp` | Couvert structurellement |
| 18 | Matrice preuves/compétence | `MATRICE_COMPETENCES_RNCP.md` | Couvert, libellés à vérifier |
| 19 | Matière pour 4 blocs | Matrice et preuves | Partiel : preuves réelles externes requises |
| 20 | Limites signalées | Matrice + présent document | Couvert |

## Commandes de validation

```powershell
Copy-Item .env.example .env -ErrorAction SilentlyContinue
docker compose up --build -d
docker compose ps
docker compose exec backend pytest -q
docker compose exec backend ruff check app tests
docker compose exec backend mypy app
docker compose exec frontend npm test -- --run
docker compose exec frontend npm run lint
docker compose exec frontend npm run build
python scripts/smoke_test.py
```

Après les commandes, réaliser le scénario README dans une fenêtre privée et conserver les sorties/captures datées comme preuves de recette.
