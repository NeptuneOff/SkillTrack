# J-01 — Mapping import/export

## CSV d'import workout

| Champ source | Type | Obligatoire | Cible | Règle |
|---|---|---|---|---|
| date | YYYY-MM-DD | oui | workouts.performed_on | rejet si date invalide |
| workout_title | texte | oui | workouts.title | trim |
| exercise | texte | oui | workout_exercises.name | trim |
| reps | entier | oui | exercise_sets.reps | rejet si négatif |
| external_load_kg | décimal | oui | exercise_sets.external_load_kg | 0 autorisé |
| hold_seconds | entier | non | exercise_sets.hold_seconds | null si vide |
| rpe | entier 1-10 | non | exercise_sets.rpe | rejet si hors plage |

## Décision synchrone/asynchrone

- Synchrone : fichier ≤ 1 000 lignes et ≤ 2 Mo.
- Asynchrone : au-delà, création d'un `ImportJob` avec statut et rapport.
