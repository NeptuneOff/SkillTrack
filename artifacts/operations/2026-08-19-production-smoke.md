# Validation isolée du stack de production — 2026-08-19

## Périmètre exécuté

- projet Compose temporaire : `skilltrack-prodcheck` ;
- base PostgreSQL 16 et volume neufs ;
- images `production` du backend et du frontend reconstruites ;
- frontend Nginx non privilégié exposé temporairement sur `15173` ;
- backend exposé temporairement sur `18000` ;
- secrets de test dédiés injectés uniquement dans le processus de validation.

## Contrôles et résultats

| Contrôle | Résultat |
|---|---|
| `docker-compose.prod.yml` construit et démarré avec `--wait` | PASS |
| migrations Alembic sur PostgreSQL vierge | PASS |
| santé frontend `GET /healthz` | HTTP 200 |
| proxy Nginx same-origin `GET /api/health` | HTTP 200, réponse SkillTrack |
| authentification `POST /api/auth/login` | PASS, jeton JWT reçu |
| services déclarés sains par Compose | PASS |
| arrêt et suppression du volume temporaire | PASS |

Commande de principe, avec secrets remplacés avant exécution :

```powershell
$env:POSTGRES_USER='skilltrack_prodcheck'
$env:POSTGRES_PASSWORD='<secret-temporaire>'
$env:POSTGRES_DB='skilltrack_prodcheck'
$env:SECRET_KEY='<secret-temporaire-32-caracteres-minimum>'
$env:BACKEND_PORT='18000'
$env:FRONTEND_PORT='15173'
$env:PUBLIC_API_URL='/api'
docker compose --project-name skilltrack-prodcheck --file docker-compose.prod.yml `
  up --build --detach --wait --wait-timeout 180
```

Le nettoyage a été réalisé avec la cible exacte et isolée :

```powershell
docker compose --project-name skilltrack-prodcheck --file docker-compose.prod.yml `
  down --volumes --remove-orphans
```

## Limites honnêtes

Cette preuve valide les images, le réseau interne, la migration d'une base
vierge, le reverse proxy et l'authentification. Elle ne remplace pas une recette
sur l'hébergeur final avec DNS, certificat TLS, sauvegarde distante,
observabilité et test de reprise après sinistre.
