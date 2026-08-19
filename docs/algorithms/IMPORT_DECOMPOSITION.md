# S1-01 — Décomposition import CSV

```text
Entrée : fichier CSV
1. Lire les octets
2. Détecter/décoder l'encodage
3. Vérifier les colonnes obligatoires
4. Lire les lignes
5. Valider chaque ligne
6. Grouper par date + titre de séance
7. Créer séances, exercices et séries dans une transaction
8. Produire un rapport accepté/rejeté
9. Retourner le résultat ou le statut ImportJob
```

## Contrats de sortie

- Ligne valide : intégrée à une séance.
- Ligne invalide : non intégrée, erreur détaillée.
- Fichier dupliqué : rejeté par hash utilisateur.
- Erreur système : rollback complet.
