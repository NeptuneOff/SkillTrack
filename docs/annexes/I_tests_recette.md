# I — Stratégie de tests, cahier de recette et PV

## 1. Objectifs qualité

La stratégie cherche à détecter les erreurs de contrat, logique, droits d'accès, persistance, navigation et échange de données. Un pipeline vert prouve l'exécution des cas codés ; il ne prouve pas l'absence de défaut ni la validation utilisateur.

## 2. Niveaux de test

| Niveau | Outil | Portée | Seuil de sortie |
|---|---|---|---|
| Statique backend | Ruff + mypy | style, erreurs probables, types | 0 erreur |
| API/intégration | pytest + TestClient + PostgreSQL | startup, auth, CRUD, import/export, cascades | 100 % tests passants et couverture ≥ 90 % |
| Frontend composant | Vitest + Testing Library | rendu, actions utilisateur, navigation, erreurs | 100 % tests passants |
| End-to-end | Playwright | navigateur réel, routes, formulaires et téléchargements | scénario critique passant sur stack saine |
| Build | Vite | bundle de production | build réussi |
| Smoke | script Python | login + dashboard sur stack réelle | code retour 0 |
| Performance | script concurrent | dashboard authentifié | p95 < 1 000 ms, erreurs < 1 % |
| Recette | navigateur + Swagger | parcours fonctionnel complet | aucun bloquant, PV renseigné |
| Accessibilité | clavier + axe en navigateur + reflow | cinq vues connectées | 0 violation/incomplet et aucun débordement à 320 px ; lecteur d'écran en recette humaine |

## 3. Jeux d'essai prioritaires

| Domaine | Cas nominal | Cas limites/négatifs | Automatisation attendue |
|---|---|---|---|
| Auth | login démo valide | mauvais mot de passe, jeton absent/expiré | API |
| Utilisateurs | données propres | utilisateur A lit/modifie/exporte B | API multi-utilisateur |
| Séance | CRUD avec exercices | bornes min/max, séance absente, aucune série | API + UI |
| Objectif | CRUD + terminer/rouvrir | cible 0, statut invalide, objet tiers | API + UI |
| Dashboard | données connues | base vide, plusieurs semaines, `set_count > 1` | unitaire/intégration |
| Import | UTF-8 conforme | extension, >2 Mo, encodage, colonnes, date/nombres invalides | API |
| Export | CSV/JSON complet | séance sans exercice, caractères CSV, étanchéité, formule | API |
| Effacement | compte et enfants | ancien schéma/imports, jeton ensuite invalide | PostgreSQL/API |
| Navigation | toutes pages | Sessions → toute page, erreur API | frontend |
| Responsive/a11y | clavier et zoom | focus, annonce erreurs, 320 px | manuel/outillé |

## 4. Traçabilité automatisée

Les tests se trouvent dans `backend/tests/`, `frontend/src/*.test.*` et `frontend/e2e/`. La CI (`.github/workflows/ci.yml`) installe les lockfiles (`pip`/`npm ci`), exécute `pip check`, lint, typage, tests et seuil de couverture backend, tests/lint/build frontend, validation des Compose, images de production, stack réelle, smoke, benchmark et Playwright sur chaque pull request. CodeQL analyse séparément Python et JavaScript/TypeScript. Les nombres de tests doivent être lus dans la sortie finale, car ils évoluent avec les correctifs.

Commandes de preuve :

```powershell
docker compose exec -T backend ruff check app tests
docker compose exec -T backend mypy app
docker compose exec -T backend pytest -q --cov=app --cov-report=term-missing --cov-fail-under=90
docker compose exec -T frontend npm test -- --run
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm run build
docker compose --profile test run --rm e2e
python scripts/smoke_test.py
```

Conserver la sortie complète ou l'URL de CI, la date, le commit et l'environnement. Ne pas recopier un ancien résultat comme preuve de la release finale.

Derniers résultats locaux de la branche de travail, avant rattachement au commit final, le 20/08/2026 :

| Contrôle | Résultat | Portée notable |
|---|---|---|
| Backend PostgreSQL | **21/21 cas passants, couverture applicative 92,33 %, zéro warning pytest** | auth, CRUD, repository substitué, non-régression seed, ordre persistant des séries, MailHog, imports/rollback, isolation, exports/round-trip, effacement, migrations/contraintes/trigger et documentation CSP |
| Frontend Vitest | **10/10 passants** | vrais composants, 401, CRUD, import/historique/exports, profil, navigation et axe |
| Frontend qualité | **ESLint et build verts** | source et bundle de production |
| Playwright Chromium | **2/2 scénarios passants** | jury : login/dashboard, CRUD, objectif, import/rapport, téléchargements, profil/nettoyage ; accessibilité : axe réel sur cinq vues, clavier et reflow 320 px |
| Smoke stack réelle | **9/9 contrôles passants, nettoyage vert** | santé/en-têtes, JWT, profil/dashboard, CRUD, MailHog, exports, import partiel/rapport ; JSON local sous `artifacts/validation/` et artefact CI prévu |
| Compose/Alembic | **dev + production builds/health verts, révision `20260820_04` en tête** | modèles Compose, images et PostgreSQL réel |
| Performance finale | **200/200, p95 124,74 ms, seuil 1 000 ms** | 20 utilisateurs concurrents simulés ; artefact `2026-08-20-rncp-captures-final.json` |
| Audit nettoyage E2E | **0 trace résiduelle** | aucun objet E2E dans `workouts`, `goals` ou `import_jobs` |

Associer ces résultats au hash du commit final et à la sortie `verify`/CI dans le dossier.

Le calcul de couverture exclut les fichiers de révision Alembic, exécutés en sous-processus ; leur état, les contraintes et le trigger sont néanmoins vérifiés explicitement sur PostgreSQL par le test d'intégration du schéma et par `alembic current --check-heads`.

Preuve Playwright versionnable : `artifacts/accessibility/2026-08-19-playwright.md`.

## 5. Cahier de recette fonctionnelle

| ID | Précondition | Action | Résultat attendu | Statut final | Preuve |
|---|---|---|---|---|---|
| REC-01 | stack saine | ouvrir `/` | connexion compréhensible, compte démo indiqué | À exécuter | capture |
| REC-02 | compte démo | se connecter | dashboard visible, aucun écran vide | À exécuter | capture |
| REC-03 | connecté | parcourir chaque menu depuis chaque page | menu et contenu restent présents | À exécuter | vidéo/capture |
| REC-04 | connecté | créer séance + 2 exercices, en retirer 1 | une séance correcte persiste | À exécuter | capture + BDD/API |
| REC-05 | séance créée | modifier, détail, supprimer | modifications visibles puis 404/absence | À exécuter | capture |
| REC-06 | connecté | créer/modifier/terminer/rouvrir/supprimer objectif | cycle complet sans incohérence | À exécuter | capture |
| REC-07 | CSV exemple | importer fichier avec 1 ligne fautive | compteurs et erreur ligne affichés | À exécuter | rapport |
| REC-08 | données présentes | télécharger CSV/JSON | fichiers lisibles et complets | À exécuter | fichiers anonymisés |
| REC-09 | deux comptes de test | tenter accès croisé | refus 404/403, aucun mélange dashboard/export | À exécuter | test/log |
| REC-10 | copie de compte | effacer via Profil | compte et enfants absents ; reconnexion impossible | À exécuter | requêtes de contrôle |
| REC-11 | clavier seul | réaliser login/import/objectif | aucun blocage, focus visible | À exécuter | grille RGAA |
| REC-12 | clone propre | lancer README puis vérification | services sains, tests et smoke verts | À exécuter | journal machine vierge |

## 6. Gestion des anomalies

- Bloquant : perte/accès indu aux données, impossibilité de démarrer/se connecter/naviguer.
- Majeur : CRUD/import/export faux ou inaccessible sans contournement raisonnable.
- Mineur : défaut visuel ou libellé sans impact métier.

Tout échec reçoit : identifiant, environnement, reproduction, attendu/obtenu, cause, correction, test de non-régression, commit et résultat CI. Voir `R_doutes_bugs.md`.

## 7. Procès-verbal de recette — à signer, jamais préremplir

| Champ | Valeur à renseigner lors de la recette |
|---|---|
| Version/commit testé | |
| Date, lieu, environnement | |
| Exécutant | |
| Représentant utilisateur/commanditaire | |
| Scénarios réussis/total | |
| Anomalies ouvertes et réserves | |
| Décision | Accepté / accepté avec réserves / refusé |
| Nom, rôle et signature du valideur | |

Une CI verte ne remplace pas ce PV. La signature et l'acceptation doivent venir d'une personne réelle habilitée.
