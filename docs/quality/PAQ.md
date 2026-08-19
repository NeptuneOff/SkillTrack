# F-01 — Plan d'assurance qualité

## Standards et outils

| Domaine | Outil | Seuil |
|---|---|---|
| Python style | Ruff | 0 erreur bloquante |
| Typage Python | mypy | 0 erreur sur `app` |
| Tests backend | pytest | succès complet |
| Couverture | pytest-cov | objectif 80 % sur services critiques |
| Frontend | ESLint + TypeScript | 0 erreur |
| Complexité | Radon | fonction critique ≤ B |
| CI | GitHub Actions | pipeline vert avant merge |

## Definition of Done

- Exigence liée à une user story.
- Tests unitaires ou d'intégration ajoutés.
- Aucune régression CI.
- Documentation mise à jour si contrat API ou procédure modifiée.
- Risques sécurité/RGPD vérifiés si données utilisateur concernées.
