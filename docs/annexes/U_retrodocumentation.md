# U — Rétrodocumentation de l'existant SkillTrack

## 1. Objet et méthode

Cette analyse a été reconstruite à partir du code et de l'historique Git, sans supposer l'intention de l'auteur. Sources : arbre du commit initial `d0ca5b5`, diff vers la branche RNCP, modèles, routes, contrats et environnement final. Les faits observés sont séparés des recommandations.

## 2. Évolution observée

| Aspect | État initial `d0ca5b5` | État actuel observé | Impact |
|---|---|---|---|
| Backend | architecture routes/services/repositories annoncée | monolithe compact, services métier + port repository/adaptateur SQLAlchemy | séparation du stockage effective, routeur encore centralisé |
| Frontend | React/TypeScript annoncé | React JSX/Vite, pages en composants | interface plus riche, typage réduit |
| Données | schéma initial et migrations SQL | modèles actuels + révisions Alembic canoniques | ancien volume conservé, évolution versionnée |
| Fonctionnel | périmètre documenté | CRUD séances/objectifs, dashboard, import/export/profil | parcours jury concret |
| Preuves | nombreux modèles documentaires | annexes alignées sur l'implémentation réelle | évite les preuves « à remplir » non expliquées |
| CI | Python/Node/Postgres | Node 22 et lifecycle TestClient corrigés | environnement distant aligné |
| Seed démo | condition liée au nombre de séances | données ajoutées uniquement avec un nouveau compte démo | aucun objet supprimé ne ressuscite au redémarrage |

## 3. Architecture organique finale

```text
frontend/src/main.jsx         shell, auth, dashboard, import/export, profil
frontend/src/*Page.jsx        pages/composants métier extraits
frontend/src/api.js           client HTTP/JWT/téléchargement
backend/app/main.py           cycle de vie, routes/orchestration et transactions
backend/app/services.py       règles séances, volume et dashboard
backend/app/repositories.py   port de stockage + adaptateur SQLAlchemy/PostgreSQL
backend/app/data_exchange.py  parsing et sérialisation CSV/JSON versionnés
backend/app/notifications.py  intégration SMTP MailHog non bloquante
backend/app/migrations.py     exécution des migrations Alembic
backend/app/alembic/          révisions de schéma, contraintes et trigger
backend/app/models.py         mapping relationnel
backend/app/schemas.py        contrats et bornes
backend/app/deps.py           utilisateur courant
backend/app/core/*            config, sécurité, journalisation
docker-compose.yml            environnement local multi-tiers
```

## 4. Catalogue API

| Méthode/route | Auth | Fonction |
|---|---|---|
| GET `/health` | non | santé API |
| POST `/auth/login` | non | créer JWT |
| GET/DELETE `/users/me` | oui | profil / effacement |
| GET `/dashboard` | oui | agrégats du propriétaire |
| GET/POST `/workouts` | oui | lister/créer séances |
| GET/PUT/DELETE `/workouts/{id}` | oui | détail/modifier/supprimer séance |
| GET/POST `/goals` | oui | lister/créer objectifs |
| PUT/DELETE `/goals/{id}` | oui | modifier/supprimer objectif |
| POST `/imports/csv` | oui | importer et rapporter |
| GET `/imports/history` | oui | historique d'import |
| DELETE `/imports/history/{id}` | oui | supprimer une preuve d'import du propriétaire |
| GET `/imports/example` | oui | modèle CSV |
| GET `/exports/json` | oui | portabilité structurée |
| GET `/exports/csv` | oui | échange tabulaire |

Swagger à `http://localhost:8000/docs` fournit le contrat machine à partir des schémas.

## 5. Données et transformations

Entrées : JSON formulaires et CSV. Transformations : validation Pydantic, regroupement import, construction ORM, volume et agrégats hebdomadaires. Sorties : JSON API, fichier JSON de portabilité et CSV. Dictionnaire/MCD : `E_mcd_mpd.md`; mapping : `J_import_export.md`.

## 6. Dettes et recommandations

1. découper `main.py` en routeurs par domaine si croissance ;
2. ajouter un proxy HTTPS et un gestionnaire de secrets à la simulation production ;
3. maintenir les lockfiles Python/Node par mises à jour auditées et régénération documentée sous Python 3.12 ;
4. ajouter pagination, métriques/alertes et sauvegardes planifiées ;
5. maintenir migrations, tests multi-utilisateur, round-trip des exports et composants réels.

## 7. Rétrodocumentation d'un logiciel d'entreprise

Cette annexe prouve la méthode sur SkillTrack, mais BC04-C1 demande un logiciel existant dans une mise en situation professionnelle. Pour une preuve d'entreprise, joindre une analyse anonymisée : sources, étapes, données lues/écrites, pseudo-code, incertitudes observées/déduites, diagramme, dictionnaire et validation du référent. L'historique initial évoquait une piste Power Query → Python ; elle ne doit être utilisée que si elle correspond à une expérience réelle et est validée par le référent.
