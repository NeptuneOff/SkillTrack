# K-01 — Procédure d'intégrabilité ITIL

## Demande de changement

| Champ | Valeur |
|---|---|
| Version | release-candidate à taguer |
| Périmètre | frontend, API, BDD, scripts |
| Risques | migration BDD, régression auth, export incorrect |
| Fenêtre | créneau de test |
| Responsable | Karl Daval-Leclercq |
| Valideur | tiers à identifier |

## Critères Go/No-Go

Go uniquement si :

- tests backend verts ;
- tests frontend verts ;
- migration exécutée ;
- sauvegarde réalisée ;
- healthcheck OK ;
- smoke test OK ;
- rollback testé.

## Rollback

1. Stopper les services.
2. Restaurer le dump BDD.
3. Revenir au tag précédent.
4. Relancer `docker compose up --build -d`.
5. Exécuter `python scripts/smoke_test.py`.
6. Documenter l'incident et la décision.
