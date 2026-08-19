# SkillTrack — suivi de progression en calisthénie

SkillTrack est une application web complète destinée au suivi d'entraînement et de progression en calisthénie. Le projet sert de support technique et documentaire pour le RNCP 36463 CDA Numérique niveau 6.

## Direction artistique

L'interface utilise une identité visuelle originale : **Nocturne Kinetic**. Le style repose sur un fond sombre bleu/noir, des cartes translucides, des accents menthe/cyan et une logique de tableau de bord sportif moderne. L'objectif est de donner une impression de précision, de progression et d'analyse technique.

## Fonctionnalités livrées

- Authentification JWT.
- Utilisateur de démonstration créé au démarrage.
- Tableau de bord avec statistiques globales et hebdomadaires.
- CRUD complet des séances.
- Ajout de séries/exercices avec volume automatique.
- Objectifs sportifs et suivi de progression.
- Import CSV avec rapport d'import.
- Export CSV et JSON.
- Profil utilisateur avec export/suppression des données.
- API documentée par Swagger.
- Docker Compose : frontend, backend, PostgreSQL, MailHog.
- Tests backend et frontend.
- Documentation RNCP complète dans `/docs`.

## Démarrage rapide

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Accès :

- Frontend : http://localhost:5173
- API Swagger : http://localhost:8000/docs
- MailHog : http://localhost:8025

Compte démo :

- Email : `demo@skilltrack.dev`
- Mot de passe : `DemoPassword123!`

## Tests

Backend :

```powershell
docker compose exec backend pytest
```

Frontend :

```powershell
docker compose exec frontend npm test -- --run
```

Smoke test :

```powershell
python scripts/smoke_test.py
```

## Format CSV importable

```csv
date,title,exercise,reps,load_kg,duration_seconds,difficulty,notes
2026-08-19,Push technique,Tuck planche,12,0,30,7,bon contrôle scapulaire
```

## Preuves RNCP

Les preuves sont organisées dans `/docs/rncp` et `/docs/annexes` : cahier des charges, backlog, architecture, MCD/MPD, sécurité, RGPD, RGAA, RSE, tests, recette, import/export, ITIL, réingénierie, documentation anglaise, matrice de compétences.

## Scénario de démonstration jury (10 à 15 minutes)

1. Vérifier `docker compose ps`, puis ouvrir le frontend.
2. Se connecter avec le compte de démonstration.
3. Présenter les métriques réelles et les huit semaines du dashboard.
4. Créer une séance, ajouter deux exercices, en supprimer un puis enregistrer.
5. Modifier la séance enregistrée, consulter son détail, puis la supprimer en fin de démonstration.
6. Créer un objectif mesurable, le modifier, le terminer puis montrer sa suppression.
7. Télécharger le CSV d'exemple, l'importer et commenter le rapport d'erreur ligne par ligne.
8. Télécharger les exports CSV et JSON authentifiés.
9. Montrer les droits d'export et d'effacement dans Profil, sans supprimer le compte avant la fin.
10. Ouvrir Swagger, exécuter les tests, puis relier les preuves à `docs/rncp/MATRICE_COMPETENCES_RNCP.md`.
11. Présenter MailHog comme service d'intégration ; préciser honnêtement qu'aucun parcours e-mail métier complet n'est encore livré.

## Validation avant soutenance

```powershell
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

La grille détaillée des 20 contrôles et les limites restantes sont documentées dans `docs/rncp/CONTROLE_FINAL.md`. `bcrypt==4.0.1` est volontairement verrouillé pour rester compatible avec Passlib, et l'image frontend utilise Node 22.
