# J — Interface d'échange : mapping CSV/JSON

## 1. Contrat d'import CSV

- transport : `multipart/form-data`, champ `file` ;
- extension `.csv`, taille maximale 2 000 000 octets ;
- encodage UTF-8 ou UTF-8 avec BOM ;
- première ligne : en-têtes normalisés ; séparateur virgule ou point-virgule détecté ;
- traitement synchrone et transaction globale ; regroupement legacy par `(date, title)` ou format complet par `workout_id` ;
- réponse JSON : statut, lignes importées/rejetées/ignorées, séances/objectifs créés et erreurs ;
- historique : 20 derniers traitements du propriétaire, supprimables individuellement via `DELETE /imports/history/{id}` avec contrôle `owner_id`.

Endpoint : `POST /imports/csv` (`backend/app/main.py:import_csv`). Parseur : `backend/app/data_exchange.py:parse_csv_import`. Exemple téléchargeable : `GET /imports/example` et `samples/import_workouts.csv`.

## 2. Table de correspondance import

| Champ CSV | Obligatoire | Conversion | Cible | Défaut/règle de rejet |
|---|---|---|---|---|
| `date` | oui | ISO `YYYY-MM-DD` → date | `Workout.date` | date invalide → ligne rejetée |
| `title` | oui | texte | `Workout.title` | absent/en-tête manquant → fichier rejeté ; borne Pydantic |
| `exercise` | oui | texte | `TrainingSet.exercise` | absent/en-tête manquant → fichier rejeté ; borne Pydantic |
| `type` | non | texte | `Workout.type` | `Import` si vide |
| `intensity` | non | entier | `Workout.intensity` | 6 si vide ; 1..10 via schéma |
| `duration_minutes` | non | entier | `Workout.duration_minutes` | 60 si vide ; 1..1440 |
| `workout_notes` | non | texte | `Workout.notes` | `Import CSV` si vide |
| `category` | non | texte | `TrainingSet.category` | `autre` si vide |
| `set_count` | non | entier | `TrainingSet.set_count` | 1 si vide ; 1..50 |
| `reps` | non | entier | `TrainingSet.reps` | 0 si vide ; jamais négatif |
| `load_kg` | non | décimal | `TrainingSet.load_kg` | 0 si vide ; jamais négatif |
| `duration_seconds` | non | entier | `TrainingSet.duration_seconds` | 0 si vide |
| `difficulty` | non | entier | `TrainingSet.difficulty` | 5 si vide ; 1..10 |
| `assistance_kg` | non | décimal | `TrainingSet.assistance_kg` | 0 si vide |
| `set_notes` | non | texte | `TrainingSet.notes` | chaîne vide ; `notes` accepté en format legacy |

Le format complet ajoute `record_type` et accepte les types `metadata`, `profile`, `workout`, `training_set`, `goal` et `import`. Les lignes metadata/profile/import sont comptées comme ignorées ; séances, exercices et objectifs sont reconstruits. Cette distinction permet le réimport de l'export sans recréer l'identité ou l'historique technique.

## 3. Exemple

```csv
date,title,type,intensity,duration_minutes,workout_notes,exercise,category,set_count,reps,load_kg,duration_seconds,difficulty,assistance_kg,set_notes
2026-08-19,Push technique,Push,7,60,Séance contrôlée,Tuck planche,statique,3,0,0,20,7,0,Bon contrôle
```

## 4. Règles d'erreur et atomicité

| Niveau | Comportement attendu |
|---|---|
| Fichier | mauvaise extension, taille, encodage ou colonnes → HTTP 4xx, aucune importation |
| Ligne | conversion/validation impossible → rejet avec numéro de ligne |
| Groupe | lignes valides de même date/titre → une séance et plusieurs exercices |
| Système | exception SQLAlchemy → rollback global et HTTP 500 ; aucune donnée du fichier enregistrée |

La stratégie actuelle accepte les lignes valides malgré les lignes rejetées. Ce choix doit être visible dans l'interface et validé par l'utilisateur.

## 5. Contrat d'export CSV

Le CSV vise la réutilisation dans un tableur ou une autre instance. Il commence par un BOM UTF-8 et utilise un schéma versionné de 46 colonnes. Une ligne porte un `record_type` : métadonnées, profil, séance, exercice, objectif ou import. Une séance possède sa propre ligne et reste donc représentable sans exercice. Les cellules commençant par `=`, `+`, `-`, `@`, tabulation ou retour chariot sont préfixées pour neutraliser les formules tableur, puis restaurées lors d'un réimport SkillTrack.

Contrôles : Content-Type CSV, `Content-Disposition`, UTF-8 BOM, échappement des virgules/guillemets/retours ligne, profil, toutes séances/exercices, objectifs et imports du propriétaire, et round-trip des données métier. Source : `backend/app/data_exchange.py:CSV_FIELDS` et `build_csv_export`.

## 6. Contrat d'export JSON RGPD

Structure cible versionnée :

```json
{
  "metadata": {
    "format": "skilltrack-data-export",
    "schema_version": "1.0",
    "api_version": "1.1.0",
    "exported_at": "ISO-8601 UTC",
    "scope": "all_user_data",
    "counts": {}
  },
  "profile": {},
  "workouts": [{"sets": []}],
  "goals": [],
  "imports": []
}
```

L'export ne sérialise ni `password_hash`, ni jeton, ni représentation d'objet Python. Les dates passent par l'encodeur FastAPI, les listes sont exhaustives et chaque requête est filtrée par propriétaire. Source : `backend/app/data_exchange.py:build_json_export`.

## 7. Matrice de tests d'interopérabilité

- import exemple nominal puis comparaison champs source/cible ;
- virgule, guillemet, accent et retour ligne dans notes ;
- séance sans exercice dans export ;
- plusieurs lignes regroupées ;
- valeurs aux bornes et au-delà ;
- export utilisateur A sans identifiant de B ;
- JSON parsable et aucun marqueur de représentation objet ;
- réimport du CSV exporté, vérification des séances/exercices/objectifs et comptage explicite des lignes techniques ignorées.
