# Matrice de preuves RNCP 36463

> Les formulations ci-dessous sont descriptives et provisoires : elles doivent être rapprochées du référentiel officiel transmis par l'organisme certificateur. Une preuve dans ce dépôt facilite la soutenance mais ne vaut pas, à elle seule, validation par le jury.

Statuts : **couvert** = code, interface, test ou document identifiable ; **partiel** = preuve présente mais insuffisante ; **à compléter** = preuve externe ou travail supplémentaire requis.

## Bloc 1 — Cadrage et conception (9 compétences descriptives)

| # | Compétence descriptive | Preuves / fichiers | Fonctionnalité | État | Amélioration recommandée |
|---|---|---|---|---|---|
| 1 | Analyser un besoin métier | `docs/annexes/A_cahier_des_charges.md` | Périmètre SkillTrack | Couvert | Ajouter comptes rendus d'entretiens réels |
| 2 | Identifier utilisateurs et parcours | `docs/annexes/B_backlog_user_stories.md`, frontend | Parcours sportif/jury | Partiel | Tests utilisateurs datés |
| 3 | Formaliser les exigences | Cahier des charges, README | Critères fonctionnels | Couvert | Versionner les changements d'exigences |
| 4 | Prioriser un backlog | `docs/annexes/B_backlog_user_stories.md` | User stories | Partiel | Ajouter critères DoR/DoD et vélocité |
| 5 | Planifier le projet | `docs/annexes/C_planning.md` | Jalons | Partiel | Ajouter réalisé vs prévisionnel |
| 6 | Concevoir l'architecture | `docs/annexes/D_architecture.md`, `docker-compose.yml` | Architecture 3 tiers | Couvert | Ajouter ADR sur les choix récents |
| 7 | Modéliser les données | `docs/annexes/E_mcd_mpd.md`, `models.py` | Utilisateurs/séances/objectifs | Couvert | Aligner le diagramme sur les nouveaux champs |
| 8 | Concevoir l'UX et l'accessibilité | `docs/DIRECTION_ARTISTIQUE.md`, `H_RGAA.md`, frontend | Nocturne Kinetic | Partiel | Audit RGAA outillé et tests utilisateurs |
| 9 | Évaluer risques, sécurité et RGPD | `F_securite.md`, `H_RGPD.md` | JWT, isolation, droits | Couvert | Ajouter analyse de menace datée |

## Bloc 2 — Développement applicatif (9 compétences descriptives)

| # | Compétence descriptive | Preuves / fichiers | Fonctionnalité | État | Amélioration recommandée |
|---|---|---|---|---|---|
| 10 | Développer une interface web | `frontend/src/main.jsx`, CSS | Toutes pages | Couvert | Découper en composants/TypeScript |
| 11 | Créer des formulaires validés | Frontend, `schemas.py` | Séances/import/login | Couvert | Afficher les erreurs champ par champ |
| 12 | Développer une API REST | `backend/app/main.py`, Swagger | CRUD/API | Couvert | Découper les routeurs |
| 13 | Implémenter la logique métier | `services.py` | Volume/dashboard | Couvert | Tests unitaires du calcul |
| 14 | Accéder à une base relationnelle | `models.py`, `db.py` | Persistance PostgreSQL | Couvert | Introduire Alembic |
| 15 | Gérer les relations de données | Modèles SQLAlchemy | Séance → exercices | Couvert | Modéliser exercice → séries séparément |
| 16 | Authentifier et autoriser | `security.py`, `deps.py` | JWT/propriétaire | Couvert | Rotation/révocation des jetons |
| 17 | Importer et valider des données | Route `/imports/csv`, tests | CSV + rapport | Couvert | Import transactionnel configurable |
| 18 | Exporter des données | Routes `/exports/*`, client API | CSV/JSON/RGPD | Couvert | Ajouter version du format |

## Bloc 3 — Qualité, tests et déploiement (9 compétences descriptives)

| # | Compétence descriptive | Preuves / fichiers | Fonctionnalité | État | Amélioration recommandée |
|---|---|---|---|---|---|
| 19 | Définir une stratégie de tests | `docs/annexes/I_tests_recette.md` | Plan de tests | Couvert | Ajouter seuil de couverture |
| 20 | Écrire des tests backend | `backend/tests/test_api.py` | Auth/CRUD/import/export | Couvert | Isolation complète via fixtures |
| 21 | Écrire des tests frontend | `frontend/src/app.test.jsx` | Formulaire | Partiel | Tester les composants réels, pas un harnais |
| 22 | Réaliser une recette | `docs/annexes/I_tests_recette.md` | Scénarios | Partiel | Joindre captures et PV signé |
| 23 | Automatiser la qualité | `.github/workflows/ci.yml` | lint/type/test/build | Couvert | Verrouiller les versions npm |
| 24 | Conteneuriser l'application | Dockerfiles, Compose | 4 services | Couvert | Images production sans reload |
| 25 | Déployer de façon reproductible | README, scripts setup | Installation | Couvert | Tester sur machine vierge |
| 26 | Mesurer les performances | `docs/annexes/Q_performance.md` | Protocole | Partiel | Conserver résultats chiffrés reproductibles |
| 27 | Appliquer éco-conception/RSE | `docs/annexes/H_RSE.md` | Démarche | Partiel | Mesures avant/après |

## Bloc 4 — Maintenance, exploitation et collaboration (9 compétences descriptives)

| # | Compétence descriptive | Preuves / fichiers | Fonctionnalité | État | Amélioration recommandée |
|---|---|---|---|---|---|
| 28 | Documenter l'installation | README FR/EN | Prise en main | Couvert | Vidéo courte de secours |
| 29 | Documenter l'utilisation | README, scénario jury | Parcours complet | Couvert | Guide illustré |
| 30 | Documenter le code et l'API | Swagger, annexes architecture/code | API | Couvert | Docstrings systématiques |
| 31 | Organiser la maintenance | `K_ITIL_deploiement.md` | Exploitation | Partiel | Runbook incident réel |
| 32 | Diagnostiquer les anomalies | `R_doutes_bugs.md` | Registre bugs | Partiel | Lier chaque bug à commit/test |
| 33 | Assurer traçabilité Git | `O_git_tracabilite.md`, historique Git | Versions | Partiel | Nettoyer l'important worktree actuel |
| 34 | Collaborer et communiquer | `T_collaboration.md` | Organisation | Partiel | Preuves externes d'équipe nécessaires |
| 35 | Conduire l'amélioration continue | `U_retrodocumentation.md` | Rétrospective | Partiel | KPI et actions closes |
| 36 | Capitaliser/réutiliser | Annexes architecture/algorithmes | Services et documentation | Partiel | Extraire composants réutilisables |

## Limites honnêtes à présenter

- Les intitulés officiels des 36 compétences doivent être validés avec le référentiel officiel.
- L'application reste un monolithe de démonstration ; l'API et le frontend nécessitent un découpage avant croissance.
- La migration de compatibilité intégrée facilite la démonstration, mais une exploitation réelle doit utiliser Alembic.
- MailHog est présent dans l'architecture sans parcours e-mail métier complet.
- Les preuves entreprise, collaboration réelle, mesures de performance et PV de recette doivent venir de situations authentiques ; elles ne peuvent pas être fabriquées dans ce dépôt.
