# Audit d’accessibilité navigateur — 19 août 2026

## Périmètre et environnement

- release candidate locale SkillTrack ;
- Chromium Playwright `1.62.1` dans l’image officielle ;
- interface réelle connectée à FastAPI et PostgreSQL ;
- moteur axe-core exécuté dans le navigateur, règles par défaut incluant les contrastes ;
- parcours au clavier et reflow à `320 px`, équivalent à un zoom de 400 % sur une fenêtre de `1280 px`.

Commande reproductible :

```powershell
docker compose --profile test run --rm e2e npx playwright test e2e/accessibility.spec.js
```

## Résultats

| Vue | Règles axe validées | À revoir | Violations |
|---|---:|---:|---:|
| Dashboard | 35 | 0 | 0 |
| Séances | 39 | 0 | 0 |
| Objectifs | 39 | 0 | 0 |
| Import / Export | 41 | 0 | 0 |
| Profil RGPD | 35 | 0 | 0 |

Contrôles complémentaires réussis :

- lien d’évitement atteint et activé au clavier ;
- champs email, mot de passe et bouton de connexion parcourus avec `Tab`, connexion avec `Entrée` ;
- chaque entrée de navigation activée avec `Entrée` et titre de page contrôlé ;
- aucune vue ne provoque de débordement horizontal du document à `320 px` ;
- le rapport Playwright attache le résultat axe JSON de chaque vue et une capture du reflow.

Les premiers passages ont révélé le bloc d’exemple CSV à `655 px`, puis la table d’historique à `725 px` avec sept lignes réelles, des attributs ARIA non applicables et des contrastes impossibles à déterminer à cause des dégradés. Les conteneurs ont été rendus réductibles, les surfaces déterministes, les rôles corrigés et le bloc CSV rendu cassable ; la non-régression attend la fin des chargements et échoue aussi sur tout résultat axe « incomplete ».

## Limite annoncée

Ce contrôle automatisé robuste ne remplace pas une recette humaine avec NVDA, JAWS ou VoiceOver. Une session lecteur d’écran reste recommandée avant une mise en production publique ; elle n’est pas présentée ici comme déjà réalisée.
