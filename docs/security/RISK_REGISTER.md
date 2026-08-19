# G-01 — Registre des risques SkillTrack

Score = probabilité x impact, de 1 à 25.

| ID | Actif | Scénario | P | I | Brut | Mesure | Résiduel | Preuve |
|---|---|---|---:|---:|---:|---|---:|---|
| R-01 | Compte | Mot de passe compromis | 3 | 5 | 15 | bcrypt, longueur, JWT expiré | 8 | test auth |
| R-02 | Données | Accès à une séance d'un autre utilisateur | 3 | 5 | 15 | filtre user_id systématique | 4 | test accès croisé |
| R-03 | Import | CSV malformé inséré partiellement | 4 | 4 | 16 | validation, transaction, rapport | 6 | test import invalide |
| R-04 | Export | Export de données hors propriétaire | 2 | 5 | 10 | repository filtré | 3 | test export |
| R-05 | Disponibilité | BDD indisponible | 2 | 4 | 8 | healthcheck, rollback, sauvegarde | 4 | procédure ITIL |
| R-06 | RGPD | Conservation excessive | 2 | 4 | 8 | durée définie, suppression | 4 | registre RGPD |
| R-07 | Injection | Entrée utilisateur dangereuse | 2 | 5 | 10 | ORM, Pydantic | 3 | tests négatifs |
| R-08 | Dépendance | Vulnérabilité package | 3 | 4 | 12 | CI, SBOM, veille | 6 | rapport dépendances |
