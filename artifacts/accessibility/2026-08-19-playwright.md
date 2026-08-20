# Preuve Playwright et accessibilité — 2026-08-19

Commande exécutée contre le stack Docker Compose relié à PostgreSQL :

```powershell
docker compose --profile test run --rm e2e
```

Résultat final : **2 tests réussis sur 2** dans Chromium.

## Parcours jury

Le scénario `frontend/e2e/jury-flow.spec.js` vérifie l'authentification, la
navigation, les CRUD séances/exercices/objectifs, la fin d'un objectif,
l'import CSV avec une ligne rejetée, le rapport d'erreur, les trois
téléchargements, le profil RGPD et le nettoyage des données créées.

## Audit accessibilité réel

Le scénario `frontend/e2e/accessibility.spec.js` exécute axe-core dans le vrai
navigateur, attend la fin des chargements et inclut l'historique d'import réel.

| Vue | Règles axe validées | Incomplètes | Violations |
|---|---:|---:|---:|
| Dashboard | 35 | 0 | 0 |
| Séances | 39 | 0 | 0 |
| Objectifs | 39 | 0 | 0 |
| Import / Export | 41 | 0 | 0 |
| Profil RGPD | 35 | 0 | 0 |

Le même scénario valide aussi :

- l'accès clavier au lien d'évitement, aux champs et à la navigation ;
- le focus du contenu principal après navigation ;
- l'absence de débordement horizontal des cinq vues à 320 px, équivalent au
  reflow demandé à 400 % sur une largeur de référence de 1 280 px.

Ces contrôles automatiques renforcent la preuve RGAA mais ne remplacent pas une
recette manuelle complète avec plusieurs lecteurs d'écran et utilisateurs en
situation de handicap.
