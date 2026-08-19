# Sauvegardes locales

Exécuter `scripts/backup.ps1` ou `scripts/backup.sh` pour générer ici une
sauvegarde PostgreSQL accompagnée de son empreinte SHA-256.

Les fichiers `*.dump` contiennent des données personnelles et sont ignorés par
Git. Seul ce mode opératoire est versionné.

Une sauvegarde peut être contrôlée sans toucher à la base courante :

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify_backup.ps1 `
  -BackupPath artifacts\backups\skilltrack-YYYYMMDD-HHMMSS.dump
```

Le contrôle restaure le dump dans une base temporaire au nom aléatoire, vérifie
les tables principales, puis supprime uniquement cette base temporaire.
