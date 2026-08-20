# H-RSE — Écoconception et responsabilité

## 1. Périmètre

La démarche couvre le MVP local : frontend, API, PostgreSQL, images Docker et dépendances. Aucune mesure d'énergie ou d'impact carbone n'a été réalisée ; ne pas convertir temps de réponse ou poids d'image en CO₂ sans méthode reconnue.

## 2. Décisions déjà observables

| Décision | Effet attendu | Preuve | Limite |
|---|---|---|---|
| Application 3 tiers + SMTP de développement | évite une orchestration distribuée inutile | `docker-compose.yml`, architecture | quatre services restent démarrés en développement |
| Images multi-stage Alpine/slim | sépare développement et runtime | Dockerfiles + `docker-compose.prod.yml` | taille finale à mesurer |
| Pas de polling | réduit requêtes inutiles | frontend charge à la navigation/action | à confirmer par DevTools |
| Icônes vectorielles | évite un catalogue bitmap | `lucide-react` | poids du bundle à mesurer |
| Agrégats à la demande | pas de tâche permanente | `/dashboard` | calcul en mémoire moins efficace à grande échelle |
| Historique import limité à 20 | borne une réponse | `backend/app/main.py:import_history` | listes séances/objectifs non paginées |
| Données locales, aucun tracker | limite transferts tiers | revue de `api.js` | déploiement futur à réévaluer |
| MailHog réservé au développement | prouve SMTP sans fournisseur ni e-mail réel | Compose + notification objectif | service absent du profil production |

## 3. Indicateurs à mesurer par release

| Indicateur | Baseline | Cible | Commande/preuve |
|---|---:|---:|---|
| Bundle JS/CSS gzip | JS 70 154 octets + CSS 2 485 octets (build du 19/08) | suivre et éviter +10 % sans justification | fichiers `frontend/dist/assets` mesurés en mémoire |
| Requêtes dashboard initial | à mesurer | ≤ 5 utiles | HAR DevTools |
| p95 dashboard, 20 utilisateurs | 124,74 ms au verify final le 20/08/2026 | < 1 000 ms | `artifacts/performance/2026-08-20-rncp-captures-final.json` |
| Erreurs benchmark | 0/200 | < 1 % | même artefact |
| Taille images Docker | à mesurer | tendance stable ou baisse | `docker image ls` export daté |
| CPU/RAM au repos et sous test | à mesurer | baseline puis régression <20 % | `docker stats --no-stream` |

Le benchmark final a été relancé après rebuild ; il reste une mesure locale, pas un engagement de production. Voir `Q_performance.md`.

## 4. Plan d'amélioration priorisé

1. maintenir les lockfiles Python/Node, l'audit npm actuellement à 0 vulnérabilité, `pip check` et les mises à jour Dependabot ;
2. mesurer les images multi-stage et retirer les outils inutiles du runtime ;
3. paginer les listes et streamer les exports volumineux ;
4. mesurer bundle, requêtes, images, CPU/RAM avant optimisation ;
5. supprimer dépendances/assets inutilisés et documenter le gain avant/après.

## 5. Dimension sociale et inclusive

La RSE inclut l'accessibilité et les conditions de travail : documentation FR/EN, procédure reproductible, messages d'erreur actionnables et audit RGAA. Une évaluation par des utilisateurs ou collaborateurs en situation de handicap reste une validation externe nécessaire, jamais une hypothèse.
