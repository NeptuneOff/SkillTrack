# A — Cahier des charges et spécifications

## 1. Identification du livrable

| Champ | Valeur |
|---|---|
| Produit | SkillTrack, application web de suivi de progression en calisthénie |
| Version documentaire | 1.0 — 19 août 2026 |
| Nature | MVP pédagogique et démonstrateur technique RNCP 36463 |
| Porteur | Karl — projet individuel |
| Utilisateurs visés | Pratiquants débutants ou intermédiaires ; jury lors de la démonstration |
| Source du besoin | Demande du porteur de projet ; aucun entretien utilisateur externe n'est encore joint |

SkillTrack remplace un suivi dispersé dans un carnet ou un tableur par un parcours unique : authentification, saisie des séances et exercices, objectifs mesurables, statistiques, import et portabilité des données.

## 2. Problème et résultats attendus

Un pratiquant doit pouvoir comprendre l'application sans explication orale et retrouver des données fiables qui lui appartiennent. Les résultats attendus sont :

1. démarrer l'environnement local de manière reproductible ;
2. s'authentifier avec un jeton limité dans le temps ;
3. consulter un tableau de bord calculé depuis PostgreSQL ;
4. créer, lire, modifier et supprimer une séance et ses exercices ;
5. créer, modifier, terminer, rouvrir et supprimer un objectif ;
6. importer un CSV UTF-8 et obtenir un rapport ligne par ligne ;
7. exporter les données du propriétaire en CSV et JSON ;
8. exercer les droits d'accès, portabilité et effacement ;
9. empêcher l'accès aux objets d'un autre utilisateur ;
10. fournir au jury des tests, une CI et une documentation traçable.

## 3. Périmètre

### Inclus

- application web responsive React/Vite ;
- API REST FastAPI et documentation OpenAPI/Swagger ;
- PostgreSQL 16 via SQLAlchemy ;
- authentification JWT, hachage bcrypt et filtrage `owner_id` ;
- saisie UI de séances avec une ou plusieurs lignes d'exercice/séries ; l'API conserve aussi le cas historique sans exercice ;
- objectifs avec valeur actuelle, valeur cible, unité, priorité et statut ;
- agrégats du dashboard ;
- import CSV synchrone limité à 2 Mo, rapport d'erreurs et historique ;
- exports CSV/JSON authentifiés et suppression du compte ;
- notification MailHog non bloquante lorsqu'un objectif passe à « terminé » ;
- environnement Docker Compose, tests et CI GitHub Actions.

### Hors périmètre assumé

- création de compte publique et récupération de mot de passe ;
- coaching médical, diagnostic, biométrie ou recommandations automatisées ;
- application mobile native et mode hors ligne ;
- inscription, récupération de mot de passe et envoi d'e-mails publics ; MailHog reste un service local de développement ;
- hébergement de production, haute disponibilité, supervision 24/7 et sauvegardes opérées ;
- import asynchrone de gros volumes.

## 4. Exigences et critères d'acceptation

| ID | Priorité | Exigence | Critère observable | Preuve actuelle |
|---|---|---|---|---|
| EX-01 | Must | Connexion | identifiants valides → JWT ; invalides → 401 | `backend/app/main.py:login`, tests API |
| EX-02 | Must | Isolation | les lectures/écritures métier filtrent l'utilisateur authentifié | `backend/app/repositories.py`, `backend/app/deps.py:current_user`, test multi-utilisateur |
| EX-03 | Must | CRUD séances | création, détail, modification et suppression persistent en base | routes `/workouts`, test `test_workout_create_update_remove_sets_and_delete` |
| EX-04 | Must | Exercices | au moins un exercice guidé dans l'UI, ajout et suppression dans le formulaire | `frontend/src/WorkoutsPage.jsx`, `backend/app/schemas.py:SetIn`, tests frontend/E2E |
| EX-05 | Must | Objectifs | cycle créer/modifier/terminer/supprimer | `frontend/src/GoalsPage.jsx`, tests backend/frontend et parcours jury |
| EX-06 | Must | Dashboard | métriques calculées depuis les objets du propriétaire | `backend/app/services.py:dashboard` |
| EX-07 | Must | Import | UTF-8, 2 Mo max, colonnes requises, bilan acceptées/rejetées | `backend/app/main.py:import_csv`, tests import |
| EX-08 | Must | Portabilité | téléchargement CSV et JSON limité au propriétaire | routes `/exports/*`, tests de contenu |
| EX-09 | Must | PostgreSQL | persistance réelle et base saine au démarrage | `docker-compose.yml:2-17`, modèles SQLAlchemy |
| EX-10 | Must | Reproductibilité | `docker compose up --build -d` rend frontend/API/BDD disponibles | README, healthchecks Compose |
| EX-11 | Should | Accessibilité | labels, erreurs annoncées, clavier et reflow sans blocage | audit Chromium archivé ; lecteur d'écran humain recommandé dans `H_RGAA.md` |
| EX-12 | Should | Qualité | lint, typage, tests et build verts avant fusion | `.github/workflows/ci.yml` |
| EX-13 | Could | Messagerie | terminer un objectif → e-mail visible dans MailHog ; panne SMTP non bloquante | `backend/app/notifications.py`, test mock SMTP |

## 5. Contraintes non fonctionnelles

| Domaine | Cible | Mode de contrôle |
|---|---|---|
| Sécurité | secret hors code, mots de passe hachés, JWT expirant, CORS borné | revue configuration + tests négatifs |
| Performance | p95 dashboard < 1 000 ms à 20 utilisateurs simulés en local | `scripts/performance_test.py` et artefact daté |
| Qualité | Ruff, mypy, pytest, ESLint, Vitest et build sans échec | CI et commandes README |
| Compatibilité | navigateur moderne, Docker Desktop/Engine récent | recette sur machine cible |
| Accessibilité | cible RGAA 4.1.2/WCAG 2.1 AA sur parcours principaux | audit ciblé, clavier et outil automatisé |
| Confidentialité | minimisation, isolation, export et effacement | registre RGPD + tests multi-utilisateur |
| Maintenabilité | code typé, responsabilités documentées, ADR | revue d'architecture |

### Grille qualité ISO/IEC 25010:2023

La deuxième édition publiée en novembre 2023 définit un modèle de qualité produit à neuf caractéristiques. SkillTrack l'utilise comme grille d'analyse et de contrôle, sans revendiquer une certification. La version française de la norme n'étant pas disponible dans l'aperçu ISO, les intitulés anglais normatifs sont conservés et accompagnés d'une traduction de travail. Source primaire : [ISO/IEC 25010:2023, édition 2](https://www.iso.org/standard/78176.html).

| Caractéristique | Application SkillTrack | Preuve/contrôle |
|---|---|---|
| Functional suitability — adéquation fonctionnelle | exigences EX-01 à EX-13 et parcours métier complets | tests API/frontend/E2E + recette |
| Performance efficiency — efficience des performances | seuil et charge simultanée explicités | `Q_performance.md` et artefact JSON |
| Compatibility — compatibilité | contrats HTTP, JSON et CSV versionnés | Swagger, `J_import_export.md`, round-trip |
| Interaction capability — capacité d'interaction | titres, aides, états, feedback, inclusivité et guide | audit axe Chromium, clavier/reflow, `GUIDE_UTILISATEUR.md`; lecteur d'écran humain recommandé |
| Reliability — fiabilité | transactions, rollback, healthchecks et sauvegarde restaurée | tests rollback, Compose, runbook ITIL |
| Security — sécurité | authentification, autorisation, intégrité, minimisation et risques | `F_securite.md`, tests multi-utilisateur |
| Maintainability — maintenabilité | lint, typage, services, migrations et traçabilité | Ruff/mypy/ESLint, Alembic, CI/Git |
| Flexibility — flexibilité | configuration par environnement, conteneurs et scripts multi-OS | Compose dev/prod, variables d'environnement, setup/verify Windows/Linux |
| Safety — sûreté | prévention de pertes/corruptions et retour à un état sûr | transactions atomiques, sauvegarde/restauration vérifiée, rollback et runbook |

Chaque release relie les écarts de cette grille au backlog et au Go/No-Go. La session lecteur d'écran et la validation utilisateur restent distinctes de l'audit automatisé.

## 6. Hypothèses et dépendances

- Docker, Docker Compose et les ports 5173, 8000, 5432 et 8025 sont disponibles.
- Le compte et ses données de démonstration sont créés ensemble uniquement si le compte n'existe pas. Un redémarrage ne recrée pas une séance/un objectif supprimé ; le compte ne doit pas être conservé tel quel en production.
- La configuration fournie est une configuration locale. Les mots de passe par défaut et `SECRET_KEY` doivent être remplacés hors démonstration.
- La compatibilité d'un ancien volume est gérée par des migrations Alembic versionnées ; toute nouvelle évolution de schéma doit ajouter une révision testée.

## 7. Recherche utilisateur à réaliser

Le document ne prétend pas prouver une étude externe non effectuée. Avant le dépôt final, mener 3 entretiens de 15 minutes avec des pratiquants, anonymiser les réponses et consigner : méthode de suivi actuelle, informations réellement utilisées, irritants, utilité des exports et compréhension du vocabulaire. Une validation datée par un utilisateur pilote est requise pour transformer cette préparation en preuve.

## 8. Checklist de conformité fonctionnelle

- [x] Besoin, périmètre et hors-périmètre écrits.
- [x] Exigences traçables vers code/tests.
- [x] Contraintes techniques et limites explicites.
- [ ] Entretiens et synthèse utilisateur annexés — **validation externe requise**.
- [ ] Recette utilisateur datée et PV signé — **validation externe requise**.
- [ ] Approbation du cahier des charges par un commanditaire réel — **validation externe requise**.
