# L — Guide des preuves dans le code

Ce guide évite de recopier de longs extraits qui vieillissent. Pour la soutenance, ouvrir le symbole indiqué sur le commit final et expliquer entrée, traitement, sortie, erreur et test associé.

| Sujet | Symbole/fichier | Ce qu'il faut démontrer | Test/preuve associée |
|---|---|---|---|
| Configuration | `backend/app/core/config.py:Settings` | variables BDD, JWT, CORS, démo | `.env.example`, CI |
| Hachage/JWT | `core/security.py:hash_password`, `create_access_token`, `decode_access_token` | limite bcrypt, secret, expiration, erreur jeton | login + routes protégées |
| Utilisateur courant | `backend/app/deps.py:current_user` | identité issue du token | 401/403 sans token |
| Accès aux données | `backend/app/repositories.py:SkillTrackRepository`, `SqlAlchemySkillTrackRepository` | port substituable, requêtes et filtres propriétaire dans l'adaptateur | test dépôt substitué + PostgreSQL |
| Modèle relationnel | `backend/app/models.py` | FK, cascades, index, relations | test effacement/intégrité |
| Validation | `backend/app/schemas.py:SetIn`, `WorkoutIn`, `GoalIn` | bornes et types | tests 422 |
| Isolation séance | `main.py:get_workout/put_workout/delete_workout` | filtre `id` + `owner_id` | test multi-utilisateur |
| Cycle objectif | routes goals + `GoalsPage.jsx` | CRUD, statut et notification | test SMTP/CRUD backend, tests UI/E2E |
| Volume | `services.py:workout_volume` | formule, séries, charge/assistance, durée | cas limites algorithmes |
| Dashboard | `services.py:dashboard` | agrégats par propriétaire et semaines | test chiffres connus + benchmark |
| Import | `main.py:import_csv`, `data_exchange.py:parse_csv_import` | taille, UTF-8, dialecte, mapping, transaction, rapport | tests nominal/invalide/round-trip |
| Export | `data_exchange.py:build_json_export/build_csv_export` | exhaustivité, sécurité, version, neutralisation CSV | tests de contenu exact |
| Notifications | `notifications.py:send_goal_completed_notification` | SMTP MailHog non bloquant, logs sans e-mail | test mock SMTP |
| Migrations | `migrations.py`, `alembic/versions/*` | ancien volume → schéma canonique, contraintes/trigger | tests d'intégrité PostgreSQL |
| API frontend | `frontend/src/api.js:api` | JWT, erreur, téléchargement | tests mocks/API |
| Navigation robuste | `main.jsx:PageErrorBoundary`, `App` | route/page et erreur isolée | test Séances → Objectifs |
| Formulaire séance | composant effectif de séances | labels, exercices dynamiques, validation | test du vrai composant |
| Objectifs | composant effectif objectifs | progression, modifier/terminer/supprimer | test du vrai composant |
| Environnement | Compose dev/prod, Dockerfiles multi-stage, lockfiles Python/Node | dépendances, healthchecks, volumes, runtime durci | `pip check` + verify + smoke + E2E |
| CI | `.github/workflows/ci.yml`, `codeql.yml` | PostgreSQL réel, Node/Python, Compose, smoke, performance, E2E et analyse | URL GitHub Actions + artefacts |

## Trame d'explication orale

1. **Contrat :** quelles entrées et garanties ?
2. **Décomposition :** quelles responsabilités ?
3. **Sécurité :** où l'identité et les bornes sont-elles imposées ?
4. **Erreur :** que reçoit l'utilisateur et que devient la transaction ?
5. **Preuve :** quel test aurait échoué avant la correction ?
6. **Limite :** quelle dette reste acceptable dans le MVP ?

Les numéros de ligne sont indicatifs et peuvent bouger ; les noms de symboles et le hash du commit sont les références pérennes.
