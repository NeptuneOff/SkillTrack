# I-01 — Cahier de recette

| Scénario | Précondition | Action | Résultat attendu | Statut |
|---|---|---|---|---|
| Connexion | compte existant | login | JWT retourné | à exécuter |
| Isolation | 2 utilisateurs | lire séance autre user | 404/403 | à exécuter |
| Import valide | CSV conforme | import | lignes acceptées | à exécuter |
| Import invalide | date invalide | import | rapport d'erreur | à exécuter |
| Export JSON | séances existantes | export | JSON propriétaire | à exécuter |
| Rollback | migration test | rollback | version précédente OK | à exécuter |
