# Couverture RNCP 36463 — SkillTrack

Cette matrice relie les 36 compétences aux éléments techniques du dépôt. Elle sert de base de traçabilité pour le dossier et les annexes.

| Compétence | Preuve principale | Preuve secondaire | Statut |
|---|---|---|---|
| BC01-C1 | docs/functional/SPECIFICATION.md | docs/functional/USER_RESEARCH.md | À compléter avec entretiens |
| BC01-C2 | docs/quality/PAQ.md | pyproject.toml, frontend/.eslintrc.cjs, CI | Outillé |
| BC01-C3 | docs/architecture/C4_CONTEXT.md | docs/adr/0001-modular-monolith.md | Outillé |
| BC01-C4 | backend/app/repositories | backend/tests/test_workouts.py | Implémenté à compléter |
| BC01-C5 | docs/evidence/BUG_TEMPLATE.md | tests + CI | À documenter sur bugs réels |
| BC01-C6 | docs/performance/PERFORMANCE_PROTOCOL.md | locustfile.py | À exécuter |
| BC01-C7 | docs/accessibility/RGAA_AUDIT.md | frontend/src/styles.css | À auditer |
| BC01-C8 | docs/security/RISK_REGISTER.md | tests sécurité | À compléter |
| BC01-C9 | backend/app/services, backend/app/models.py | docs/quality/PAQ.md | Implémenté à commenter |
| BC01-C10 | backend/app/models.py, infra/sql | tests accès croisé | Implémenté partiellement |
| BC02-C1 | docs/company/P1_PROCESS_PROCEDURE.md | validation tuteur | À anonymiser/valider |
| BC02-C2 | docs/company/P2_REENGINEERING.md | mesures AS-IS/TO-BE | À mesurer |
| BC02-C3 | docs/company/P3_DOCUMENT_FLOW.md | BPMN | À compléter |
| BC02-C4 | docs/data/DATA_MODEL.md | migrations/DDL | À compléter |
| BC02-C5 | docs/company/P4_URBANIZATION.md | validation référent | À anonymiser/valider |
| BC02-C6 | docs/company/P5_REUSE_DECISION.md | ADR | À valider collectivement |
| BC02-C7 | docs/project/PLANNING.md | GitHub Projects export | À suivre |
| BC02-C8 | docs/project/AGILE_COORDINATION.md | projet robot collectif | À prouver |
| BC02-C9 | docs/testing/ACCEPTANCE.md | PV recette | À exécuter par tiers |
| BC02-C10 | docs/presentation/PRESENTATION_PLAN.md | feedback | À exécuter |
| BC02-C11 | docs/itil/INTEGRATION_PROCEDURE.md | scripts + rollback | À exécuter |
| BC02-C12 | docs/collaboration/COLLABORATION.md | PR/CR | À compléter |
| BC02-C13 | README_EN.md | pitch anglais | À relire |
| BC03-C1 | docs/evidence/TECHNICAL_SPIKE.md | sources officielles | À documenter |
| BC03-C2 | docs/algorithms/IMPORT_DECOMPOSITION.md | tests import | Outillé |
| BC03-C3 | docs/algorithms/VOLUME_ALGORITHM.md | backend/app/services/stats_service.py | Implémenté |
| BC03-C4 | docs/company/S3_ALGORITHM_EVOLUTION.md | diff avant/après | À anonymiser |
| BC03-C5 | docs/evidence/BUG_TEMPLATE.md | commit + non-régression | À documenter |
| BC03-C6 | docs/sustainability/RSE_METRICS.md | docker compose + MailHog | À mesurer |
| BC03-C7 | backend/tests | coverage.xml | Implémenté à exécuter |
| BC03-C8 | docs/project/WEEKLY_REPORT_TEMPLATE.md | GitHub Projects | À suivre |
| BC04-C1 | docs/company/U_RETRO_DOCUMENTATION.md | validation référent | À anonymiser |
| BC04-C2 | docs/import_export/MAPPING.md | sample CSV/JSON | Outillé |
| BC04-C3 | docs/privacy/RGPD_REGISTER.md | stats_service.py | Outillé |
| BC04-C4 | backend/app/services/import_service.py | export_service.py | Implémenté |
| BC04-C5 | scripts/setup.sh, scripts/setup.ps1 | CI, Docker | Implémenté à exécuter |
