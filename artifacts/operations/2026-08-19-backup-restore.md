# Preuve de sauvegarde et restauration — 19 août 2026

## Contexte

La procédure a été exécutée avant la migration corrective de la base PostgreSQL
existante. Le dump reste local et ignoré par Git, car il contient des données de
démonstration assimilables à des données personnelles.

## Résultat

- génération par `scripts/backup.ps1` : réussie ;
- format : dump PostgreSQL personnalisé ;
- empreinte SHA-256 :
  `F8E80A2059C1295A1B7635C4F8F7F8C0823D1E80BFEF4B52D4B443332736167C` ;
- restauration dans une base temporaire dédiée : réussie ;
- contrôles après restauration : 1 utilisateur, 5 séances, 5 objectifs et
  7 historiques d’import ;
- suppression de la base temporaire et du fichier temporaire du conteneur :
  réussie.

Cette vérification établit que la sauvegarde n’est pas seulement générée : elle
est effectivement restaurable. Une restauration de production resterait soumise
à une autorisation explicite et à une fenêtre de maintenance.
