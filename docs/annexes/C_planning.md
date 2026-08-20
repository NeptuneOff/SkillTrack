# C — Planning, capacité et suivi estimé/réel

## 1. Limite méthodologique

Le dépôt ne contient pas de relevé d'heures historique. Les **dates réelles** ci-dessous proviennent de Git ; les durées passées restent « non mesurées ». Les estimations de fermeture sont prospectives et ne doivent pas être présentées comme le planning initial.

## 2. Jalons observables

| Jalon | Prévision d'origine retrouvée | Réalisé vérifiable | Écart/commentaire | Preuve |
|---|---|---|---|---|
| Initialisation | non archivée | 19/08/2026 09:10 | durée inconnue | commit `d0ca5b5` |
| Refonte démonstration RNCP | non archivée | 19/08/2026 21:25 | lot très large, estimation initiale absente | commit `8492e3d` |
| Correction environnements CI | non archivée | 19/08/2026 21:33 | correctif après échec distant | commit `3fc87e0` |
| PR de validation | prévue avant fusion | PR #1 en brouillon | branche non fusionnée dans `main` au moment de ce document | GitHub PR #1 |

## 3. Plan de fermeture prévisionnel

Les charges sont des ordres de grandeur à réestimer par le réalisateur avant engagement.

| Lot | Charge estimée | Dépendance | Sortie attendue |
|---|---:|---|---|
| Corrections exports, séries, intégrité | 0,5 à 1 j | base locale disponible | code + tests backend |
| Tests frontend des vrais composants | 0,5 j | API mockée stable | tests de non-régression |
| Performance et recette technique | 0,5 j | Compose reconstruit | artefacts datés |
| Audit accessibilité ciblé | 0,5 j | interface stabilisée | rapport et correctifs |
| Dossier RNCP et répétition | 1 à 2 j | preuves techniques finales | matrice, captures, oral |
| Validations externes | selon disponibilité des tiers | utilisateur, pair, référent | CR/PV signés |

## 4. Disponibilité réelle à renseigner

Le taux officiel demandé par le référentiel ne peut pas être déduit de Git. À partir de maintenant, utiliser ce tableau sans reconstituer rétroactivement les heures :

| Date | Capacité prévue (h) | Disponible réelle (h) | Temps projet (h) | Tâches closes | Obstacle | Impact/replanification |
|---|---:|---:|---:|---|---|---|
| À renseigner | | | | | | |

Formule : `taux de disponibilité = disponible réelle / capacité prévue × 100`. Une ligne est accompagnée du lien vers l'issue, la PR ou le commit correspondant.

## 5. Gestion Agile adaptée au projet individuel

- flux Kanban : À faire → En cours (limite 1) → Revue/CI → Terminé ;
- priorité donnée aux preuves bloquantes du jury et risques forts ;
- revue à chaque lot : critères, tests, documentation, risque résiduel ;
- démonstration courte après chaque incrément utilisable ;
- rétrospective : fait, difficulté, cause, action, propriétaire, échéance.

## 6. Indicateurs de pilotage à conserver

- stories terminées / engagées ;
- taux de réussite CI ;
- couverture des scénarios critiques ;
- charge prévue / temps réel ;
- risques critiques ouverts ;
- actions de recette ouvertes/fermées.

Le pilotage collectif, les coûts et la validation par parties prenantes ne sont pas prouvés par ce seul dépôt : joindre un export de l'outil de suivi, des comptes rendus datés et des retours authentiques.
