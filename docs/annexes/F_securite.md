# F — Sécurité et registre des risques

## 1. Périmètre et méthode

Actifs : comptes, jetons, données d'entraînement, notes libres, exports et disponibilité de la base. Le score brut est `probabilité (1 à 5) × impact (1 à 5)`. Criticité : faible 1–4, modérée 5–9, élevée 10–15, critique 16–25. Le résiduel est une estimation documentaire à confirmer par tests/revue.

## 2. Registre des risques

| ID | Scénario | P | I | Brut | Prévention/détection actuelle | Résiduel estimé | Action restante |
|---|---|---:|---:|---:|---|---:|---|
| SEC-01 | Compromission du mot de passe démo | 4 | 4 | 16 | bcrypt ; secret configurable | 12 | supprimer identifiants par défaut en production, politique et rate-limit |
| SEC-02 | Vol d'un JWT stocké dans `localStorage` (XSS) | 3 | 5 | 15 | expiration, React échappe le rendu | 10 | CSP, analyse XSS, cookie HttpOnly si déploiement public |
| SEC-03 | Accès horizontal aux données d'un tiers | 3 | 5 | 15 | dépendance auth + repository filtré `owner_id` + test croisé | 6 | maintenir ce test sur toute nouvelle ressource |
| SEC-04 | Injection SQL via les entrées | 2 | 5 | 10 | ORM + Pydantic | 4 | interdire DDL dynamique hors migration ; tests d'entrées hostiles |
| SEC-05 | CSV trop gros ou malformé | 4 | 3 | 12 | extension, limite 2 Mo, UTF-8, colonnes requises, transaction atomique, rapport | 6 | ajouter une limite de lignes/temps |
| SEC-06 | Formule CSV ouverte dans un tableur | 3 | 3 | 9 | neutralisation `= + - @`, test export/réimport | 4 | maintenir les tests sur tout nouveau champ texte |
| SEC-07 | Corruption/écart de schéma | 3 | 5 | 15 | Alembic, PK/FK/CHECK/trigger, sauvegarde restaurée | 6 | tester upgrade/downgrade sur chaque révision |
| SEC-08 | Suppression RGPD incomplète | 2 | 5 | 10 | cascades BDD/ORM + test de portée incluant imports | 3 | conserver test sur ancien volume migré |
| SEC-09 | Dépendance compromise/incompatible | 4 | 4 | 16 | lockfiles Python/Node, `pip check`, Dependabot/CodeQL, bcrypt direct 5.0.0, audit npm à 0 vulnérabilité le 19/08 | 8 | audit Python/SBOM et politique de mise à jour |
| SEC-10 | CORS/secret local utilisé en production | 3 | 5 | 15 | variables `.env`, origine bornée, Compose production exige les secrets | 6 | coffre de secrets et proxy HTTPS réels |
| SEC-11 | Déni de service par login/export | 3 | 4 | 12 | taille import bornée | 9 | rate-limit, pagination/streaming, métriques |
| SEC-12 | Divulgation par logs/artefacts | 2 | 4 | 8 | `.env`/dumps ignorés, logs structurés à référence pseudonymisée | 4 | politique de conservation/purge et scan de secrets |

## 3. Mesures implémentées et preuves

| Contrôle | Preuve |
|---|---|
| Hachage/validation des mots de passe | bcrypt direct dans `backend/app/core/security.py`; limite 72 octets UTF-8 dans `schemas.py:LoginIn`; `bcrypt==5.0.0` verrouillé |
| JWT signé avec expiration | `backend/app/core/security.py:create_access_token/decode_access_token`, configuration `ACCESS_TOKEN_EXPIRE_MINUTES` |
| Authentification Bearer centralisée | `backend/app/deps.py:current_user` |
| Autorisation par propriétaire | méthodes `*_for_owner` de `backend/app/repositories.py`, appelées par toutes les routes métier |
| Validation et bornes | `backend/app/schemas.py:SetIn/WorkoutIn/GoalIn` |
| Requêtes paramétrées ORM | modèles et requêtes SQLAlchemy |
| Intégrité | FK `ON DELETE CASCADE`, `CHECK`, trigger, unicité et index dans `models.py`/Alembic |
| CORS configurable | initialisation `CORSMiddleware` dans `backend/app/main.py`, `.env.example` |
| En-têtes, cache et erreurs HTTP | middleware `security_headers` dans `backend/app/main.py` |
| Journalisation minimisée | événements structurés et référence pseudonymisée dans `core/logging.py` |
| CSV tableur | `_safe_csv_value` dans `data_exchange.py:94-105` |
| Non-régression | tests routes protégées et CI |

## 4. Menaces par frontière

```text
Navigateur (non fiable)
  └─ HTTP/JWT → API (validation + autorisation)
                  └─ ORM → PostgreSQL (contraintes + transaction)
Import CSV (non fiable) ─ validation taille/encodage/colonnes/lignes ┘
```

- le frontend n'est jamais une frontière de sécurité ;
- l'identifiant propriétaire vient du JWT, pas du corps utilisateur ;
- toute entrée fichier est hostile par défaut ;
- les exports sont des sorties sensibles et nécessitent la même autorisation que les CRUD.

## 5. Plan de traitement priorisé

1. ajouter/maintenir tests croisés à deux utilisateurs et suppression en cascade ;
2. ajouter rate-limit au login et stratégie cookie HttpOnly/CSP frontend pour une exposition publique ;
3. exécuter audit de dépendances/SBOM et traiter les alertes Dependabot/CodeQL ;
4. tester chaque migration upgrade/downgrade sur une restauration isolée ;
5. compléter l'exploitation réelle : HTTPS, coffre de secrets, alertes et procédure d'incident.

La revue sécurité par un pair et un scan daté restent requis avant de déclarer les risques résiduels acceptés.
