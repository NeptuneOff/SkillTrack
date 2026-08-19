# Matrice de preuves — RNCP 36463

## Cadre officiel et règle de lecture

Référentiel : **Concepteur développeur d'applications numériques**, niveau 6, RNCP36463, échéance d'enregistrement au 1er juin 2027. Sources primaires consultées le 19 août 2026 : [fiche France Compétences RNCP36463](https://www.francecompetences.fr/recherche/rncp/36463/) et [référentiel officiel détaillé](https://www.francecompetences.fr/wp-json/api/v1/activity/export/22659/373313). La certification comprend exactement **4 blocs et 36 compétences : 10 / 13 / 8 / 5**. L'acquisition complète est conditionnée par la validation de tous les blocs.

Les intitulés de la colonne « compétence » sont des résumés fidèles destinés à rendre la matrice lisible ; le texte opposable reste celui de France Compétences. Les modalités officielles reposent sur une mise en situation professionnelle à partir d'un **cas réel d'entreprise**, un portefeuille de livrables, un dossier de validation d'au moins 60 pages et une présentation orale de 20 minutes devant un jury professionnel. Hors VAE, le référentiel indique aussi une expérience terrain d'au moins deux mois ; un tiers-temps est prévu pour les candidats relevant d'un handicap.

Statuts stricts :

- **🟢 Démontré** : preuve interne concrète et exécutable dans le périmètre annoncé ;
- **🟠 Partiel** : livrable ou implémentation présent, mais contrôle/portée incomplet ;
- **🔴 Externe requis** : l'élément exige une situation, un acteur ou une validation réelle absente du dépôt.

Une annexe prête à remplir n'est pas une preuve réalisée. Une preuve externe ne sera jamais marquée verte sans pièce datée authentique.

## RNCP36463BC01 — Concevoir des applications numériques en intégrant les recommandations de sécurité (10)

| ID | Compétence officielle résumée fidèlement | Critère/livrable attendu | Preuves SkillTrack précises | Statut strict et reste à faire |
|---|---|---|---|---|
| BC01-C1 | Formaliser les procédures des services utilisateurs afin de recenser les résultats attendus | cahier de spécifications, procédure et checklist fonctionnelle reliés au besoin | `docs/annexes/A_cahier_des_charges.md` §§2–8 ; `docs/annexes/P_processus_et_flux.md` §2 ; backlog US-01 à US-14 | 🟢 **Démontré sur SkillTrack** — résultats, procédures, exigences et checklist formalisés ; approbation d'entreprise traitée séparément |
| BC01-C2 | Prendre en compte les impératifs utilisateurs et les recommandations qualité applicables à l'architecture logicielle | PAQ/DoD, exigences qualité, résultats de contrôles | matrice ISO/IEC 25010:2023 dans `A_cahier_des_charges.md` §5 ; DoD ; stratégie tests ; CI | 🟢 **Démontré** — neuf caractéristiques qualité de l'édition 2023 reliées à des contrôles exécutables ; périmètre accessibilité détaillé en BC01-C7 |
| BC01-C3 | Concevoir une architecture fiable adaptée à l'activité et produire du logiciel générique réutilisable | schéma d'architecture, ADR, documentation de fonctions métier | `docs/annexes/D_architecture.md` §§1–8 ; `backend/app/services.py` ; Compose dev/prod | 🟢 **Démontré** — architecture/choix/contrats réutilisables documentés dans le périmètre MVP |
| BC01-C4 | Concevoir des services d'accès aux données indépendants du stockage, sécurisés et partageables | couche/contrat d'accès, sécurité, tests de substitution/intégration | port `SkillTrackRepository` et adaptateur `SqlAlchemySkillTrackRepository` dans `backend/app/repositories.py`; utilisation dans routes/services/échanges/auth ; test `test_dashboard_business_logic_accepts_a_substituted_storage_port`; tests PostgreSQL | 🟢 **Démontré** — requêtes confinées à l'adaptateur, filtres propriétaire centralisés et logique métier testée avec un stockage substitué |
| BC01-C5 | Rechercher systématiquement erreurs et dysfonctionnements afin de livrer un logiciel déverminé | plan et jeux de tests, registre de bugs, CI, non-régressions | `docs/annexes/I_tests_recette.md` §§2–6 ; backend 20/20 et 92,32 % ; frontend 10/10 ; E2E jury + accessibilité ; `R_doutes_bugs.md`; CI | 🟢 **Démontré** — stratégie, cas réels, tests et automatisation ; limites de recette explicites |
| BC01-C6 | Estimer charge de traitement et puissance selon les utilisateurs simultanés pour anticiper l'évolution | hypothèses de volumétrie, test de charge et résultats interprétés | `scripts/performance_test.py`; `artifacts/performance/2026-08-19-verify-final.json`; `docs/annexes/Q_performance.md` | 🟢 **Démontré au niveau MVP** — verify ultime : 20 utilisateurs/200 requêtes, 100 % succès, p95 128,05 ms pour un seuil de 1 000 ms ; production à dimensionner séparément |
| BC01-C7 | Respecter une norme de présentation et réaliser des sorties adaptables/accessibles à différents handicaps | maquettes/IHM, audit RGAA, clavier, contraste, lecteur d'écran | `frontend/e2e/accessibility.spec.js`; `artifacts/accessibility/2026-08-19-browser-audit.md`; `artifacts/accessibility/2026-08-19-playwright.md`; `docs/annexes/H_RGAA.md` | 🟢 **Démontré au périmètre MVP** — Chromium axe réel : 0 violation/incomplet sur cinq vues, contrastes inclus ; clavier et reflow 320 px verts ; lecteur d'écran humain recommandé avant production |
| BC01-C8 | Identifier les risques et leur criticité afin de les prévenir | registre probabilité × impact, mesures et risque résiduel | `docs/annexes/F_securite.md` : 12 risques, scoring, contrôles et plan priorisé | 🟢 **Démontré** — analyse exploitable ; acceptation résiduelle par responsable réel à obtenir avant production |
| BC01-C9 | Produire par approche objet un code lisible, maintenable, robuste, fiable et efficace | classes/objets, règles séparées, lint, typage, tests | modèles ORM `models.py`; schémas Pydantic ; services ; Ruff/mypy/pytest dans CI ; `docs/annexes/L_extraits_code.md` | 🟢 **Démontré** — outillage et objets réels ; dette de taille du routeur documentée |
| BC01-C10 | Garantir l'intégrité et l'accès sécurisé aux données grâce aux contraintes et déclencheurs | MPD, PK/FK/unique/check, cascades, trigger actif et tests d'intégrité | `backend/app/models.py:21-133` ; `backend/app/alembic/versions/20260819_02_goal_consistency.py:upgrade` ; test `test_postgresql_schema_has_migration_constraints_indexes_and_business_trigger` | 🟢 **Démontré** — PK/FK cascade, `CHECK`, index et trigger objectif actifs et testés sur PostgreSQL |

## RNCP36463BC02 — Piloter un projet DevOps de développement d'application numérique (13)

| ID | Compétence officielle résumée fidèlement | Critère/livrable attendu | Preuves SkillTrack précises | Statut strict et reste à faire |
|---|---|---|---|---|
| BC02-C1 | Formaliser les procédures utilisateurs en contrôlant le management des processus de l'entreprise | procédure entreprise observée, contrôles de gouvernance, validation référent | procédure SkillTrack dans `docs/annexes/P_processus_et_flux.md` §§1–2 ; checklist/DoD | 🔴 **Externe requis** — cas pédagogique prêt ; procédure d'une entreprise réelle et gouvernance à joindre |
| BC02-C2 | Réingénier un processus d'entreprise selon ses règles pour améliorer résultats ou conditions de travail | AS-IS/TO-BE, indicateurs avant/après, décision et validation | `docs/annexes/P_processus_et_flux.md` §3 fournit méthode et indicateurs | 🔴 **Externe requis** — AS-IS est une hypothèse non mesurée ; situation réelle et résultats validés indispensables |
| BC02-C3 | Formaliser la circulation des documents, acteurs, rôles, rubriques et provenances | diagramme de flux et matrice documentaire validés | flux SkillTrack, tableau documents et RACI dans `docs/annexes/P_processus_et_flux.md` §§4–5 | 🔴 **Externe requis** — cartographie complète du projet, mais pas encore d'un processus d'entreprise validé |
| BC02-C4 | Modéliser une BDD adaptée aux attentes, règles de gestion, organisation et existant | MCD, MPD, dictionnaire, règles et évolution de l'existant | `docs/annexes/E_mcd_mpd.md` §§1–6 ; `backend/app/models.py`; révisions `backend/app/alembic/versions/` | 🟢 **Démontré** — modèles conceptuel/physique et migration canonique d'un schéma existant documentés |
| BC02-C5 | S'insérer dans l'urbanisation présente/future du SI avec des éléments réutilisables en couches | cartographie SI, architecture en couches, trajectoire | `docs/annexes/D_architecture.md` §§1–9 ; React/API/services/échange/ORM/PostgreSQL/SMTP ; trajectoire cible | 🟢 **Démontré sur SkillTrack** — couches et frontières réelles, interfaces et trajectoire d'urbanisation documentées ; cas d'entreprise séparé |
| BC02-C6 | Décider collectivement du degré de réutilisation, adaptation ou écriture neuve en visant la maturité CMMI | analyse d'options, compte rendu collectif et ADR | tableau de décision `docs/annexes/D_architecture.md` §7 ; dépendances et règles neuves identifiées | 🔴 **Externe requis** — décision individuelle ; revue collective datée et critères CMMI à apporter |
| BC02-C7 | Estimer les délais selon expérience, disponibilité réelle et contraintes départ/livraison | planning prévisionnel, disponibilité, prévu/réel et écarts | commits datés et plan prospectif dans `docs/annexes/C_planning.md` §§2–4 | 🟠 **Partiel** — dates Git réelles et modèle de suivi ; heures/capacité historiques non mesurées |
| BC02-C8 | Coordonner un projet Agile en maîtrisant coût, délai, qualité et risques | backlog, sprints/Kanban, comptes rendus, arbitrages et indicateurs collectifs | `docs/annexes/B_backlog_user_stories.md`; `docs/annexes/C_planning.md` §§5–6 ; PR/CI ; registre risques | 🔴 **Externe requis** — outillage d'un projet individuel ; aucune coordination d'équipe ni coûts/rituels prouvés |
| BC02-C9 | Clôturer une mission avec validation des parties concernées conformément aux préconisations CFTL | cahier de recette, anomalies, PV signé/acceptation | `docs/annexes/I_tests_recette.md` §§5–7 ; commandes et scénarios prêts | 🔴 **Externe requis** — PV volontairement vierge ; recette et signature d'un tiers requises |
| BC02-C10 | Adapter sa présentation aux décideurs à partir des contraintes pour obtenir leur adhésion | support/démonstration, feedback et décision | scénario README ; `docs/annexes/T_collaboration.md` §§3–5 ; matrice de preuves | 🔴 **Externe requis** — présentation prête, mais aucune adhésion/décision de décideur authentifiée |
| BC02-C11 | Vérifier l'intégrabilité d'un logiciel/correctif selon les bonnes pratiques ITIL et tous les points de contrôle | demande de changement, Go/No-Go, déploiement, sauvegarde/rollback testé | `docs/annexes/K_ITIL_deploiement.md`; scripts setup/verify/backup ; `artifacts/operations/2026-08-19-backup-restore.md`; `artifacts/operations/2026-08-19-production-smoke.md`; Compose/CI | 🟢 **Démontré** — sauvegarde/restauration et stack production isolées vérifiées, procédure/rollback sûrs ; décision Go d'une exploitation réelle distincte |
| BC02-C12 | Interagir efficacement en travail collaboratif, en adaptant/reformulant pour les collaborateurs handicapés | échanges, reformulations, revue, adaptation et retour authentique | protocole et registre vide dans `docs/annexes/T_collaboration.md` §§1–4 | 🔴 **Externe requis** — aucune interaction d'équipe/inclusive authentifiée jointe |
| BC02-C13 | Communiquer professionnellement en français et anglais pour partager l'information | documentation structurée bilingue et/ou présentation | `README.md`, `README_EN.md`, documentation technique, Swagger | 🟢 **Démontré à l'écrit** — relecture externe et pitch oral anglais recommandés |

## RNCP36463BC03 — Développer des applications numériques (8)

| ID | Compétence officielle résumée fidèlement | Critère/livrable attendu | Preuves SkillTrack précises | Statut strict et reste à faire |
|---|---|---|---|---|
| BC03-C1 | Utiliser les ressources disponibles ou solliciter un expert pour lever doutes et préciser le résultat | fiche de doute, sources/logs, hypothèses, décision | analyses CI et bugs dans `docs/annexes/R_doutes_bugs.md`; sources officielles RNCP ; OpenAPI et journaux CI | 🟢 **Démontré par les ressources** — plusieurs causes levées à partir de messages et environnements ; avis expert externe optionnel |
| BC03-C2 | Décomposer un problème complexe en sous-problèmes et changer d'approche pour résoudre un algorithme | analyse/pseudo-code, cas limites, alternatives, complexité | `docs/annexes/S_algorithmes.md` §§1–4 ; import décomposé taille→décodage→validation→groupement→persistance | 🟢 **Démontré** |
| BC03-C3 | Traduire une solution algorithmique dans un langage avec l'outil approprié | code exécutable correspondant au pseudo-code et tests | `backend/app/services.py:workout_volume/dashboard`; logique d'import/export ; tests API | 🟢 **Démontré** |
| BC03-C4 | Modifier un algorithme existant sans régression en comprenant son auteur | avant/après, règle changée, anciens/nouveaux tests | somme de `set_count` dans `backend/app/services.py:dashboard`; `test_dashboard_uses_real_set_count_and_volume`; refonte export dans `data_exchange.py`; `S_algorithmes.md` §5 | 🟢 **Démontré** — ancien défaut reproduit par un jeu 3+2 séries et nouveaux contrats d'échange testés |
| BC03-C5 | Corriger erreurs de code/logique en interprétant compilateur ou système pour produire un logiciel opérationnel | fiche cause racine, correctif, non-régression, CI | BUG-01 à BUG-06 dans `docs/annexes/R_doutes_bugs.md`; test navigation ; correctifs Node/TestClient/env | 🟢 **Démontré** |
| BC03-C6 | Intégrer des éléments hétérogènes/services externes pour des exécutables conformes à la politique RSE | intégration multi-technologies, service réutilisé, build et analyse RSE | React/FastAPI/PostgreSQL/Docker ; `notifications.py` + MailHog ; test SMTP non bloquant ; `docs/annexes/H_RSE.md`; images multi-stage | 🟢 **Démontré** — notification réelle sur fin d'objectif, panne isolée et service exclu du profil production |
| BC03-C7 | Préparer des jeux d'essai couvrant les possibilités pour livrer sans anomalie logique/fonctionnelle | plan, données nominales/limites/erreurs, exécution | `docs/annexes/I_tests_recette.md` §§2–5 ; backend 20/20 (92,32 %), frontend 10/10, Playwright jury + accessibilité, sample CSV et CI | 🟢 **Démontré dans le périmètre MVP** — recette humaine reste distincte |
| BC03-C8 | Estimer sa disponibilité réelle et renseigner l'outil de suivi pour rendre compte de l'avance et des impacts | capacité prévue/réelle, temps, avancement et replanification | gabarit et formule `docs/annexes/C_planning.md` §4 ; Git/PR pour avancement | 🟠 **Partiel** — disponibilité historique non relevée ; suivi doit être rempli désormais avec des valeurs réelles |

## RNCP36463BC04 — Réaliser une interface d'échange de données informatisées (5)

| ID | Compétence officielle résumée fidèlement | Critère/livrable attendu | Preuves SkillTrack précises | Statut strict et reste à faire |
|---|---|---|---|---|
| BC04-C1 | Analyser organiquement un logiciel existant par son code et ses données pour produire sa documentation technique | rétrodocumentation, architecture, routes, données, incertitudes | comparaison du commit initial et de l'existant dans `docs/annexes/U_retrodocumentation.md` §§1–6 ; Git `d0ca5b5`→branche | 🟢 **Démontré sur SkillTrack** — pour un dossier d'entreprise, ajouter le logiciel professionnel anonymisé |
| BC04-C2 | Établir analogies/différences entre données échangées grâce à des dictionnaires reconstitués | dictionnaire et table source→cible avec conversions/rejets | `docs/annexes/J_import_export.md` §§1–6 ; `docs/annexes/E_mcd_mpd.md` §3 ; sample CSV | 🟢 **Démontré** |
| BC04-C3 | Produire par agrégation/consolidation/calcul des données indisponibles, dans le respect du RGPD | algorithmes, isolation propriétaire, registre RGPD et tests | `backend/app/services.py:workout_volume/dashboard`; `docs/annexes/H_RGPD.md` §§1–6 ; tests multi-utilisateur/agrégats | 🟢 **Démontré dans le MVP** — politique de production à compléter |
| BC04-C4 | Permettre import/export interlogiciels via formats compatibles et flux synchrones/asynchrones | interface fonctionnelle, mapping, erreurs et tests interopérabilité | `/imports/csv`, `/imports/example`, `/exports/csv`, `/exports/json`; `docs/annexes/J_import_export.md`; tests API | 🟢 **Démontré en synchrone** — gros volumes/asynchrone hors périmètre explicitement |
| BC04-C5 | Écrire des scripts système pour automatiser l'installation/configuration d'un environnement de test multi-tiers | scripts shell/PowerShell, web/app/BDD, procédure vérifiée | `scripts/setup.ps1`, `scripts/setup.sh`, `scripts/verify.ps1`, `scripts/verify.sh`, `scripts/backup.ps1`, `scripts/backup.sh`; Compose ; Dockerfiles ; CI PostgreSQL | 🟢 **Démontré** — environnement multi-tiers reproductible et sauvegarde/restauration testée |

## Synthèse stricte au 19/08/2026

| Bloc | 🟢 Démontré | 🟠 Partiel | 🔴 Externe requis | Total |
|---|---:|---:|---:|---:|
| BC01 | 10 | 0 | 0 | 10 |
| BC02 | 4 | 1 | 8 | 13 |
| BC03 | 7 | 1 | 0 | 8 |
| BC04 | 5 | 0 | 0 | 5 |
| **Total** | **26** | **2** | **8** | **36** |

Cette synthèse doit être confirmée sur le commit final par la CI, `verify` et la recette. Les huit preuves externes ne deviennent vertes qu'après réalisation authentique.

## Plan de fermeture

1. rattacher au commit final l'audit navigateur, les tests 20/10/2, le smoke et le benchmark déjà exécutés ;
2. compléter la recette humaine et, avant exposition publique, la session lecteur d'écran recommandée ;
3. faire relire architecture, sécurité et décision de réutilisation par un pair ;
4. collecter un cas réel d'entreprise : procédure, AS-IS/TO-BE, documents/acteurs, mesures et validation ;
5. documenter une coordination/présentation réelle et la disponibilité dans l'outil de suivi ;
6. obtenir un PV de recette signé par une partie concernée ;
7. joindre toutes les preuves datées au dossier, puis seulement mettre à jour les statuts.

## Limites à annoncer au jury

- SkillTrack est un démonstrateur pédagogique local, pas un service de production opéré.
- Les preuves techniques sont fortes pour BC01, BC03 et BC04 ; BC02 exige davantage de faits d'entreprise et de collaboration.
- Le déploiement public, HTTPS, la gestion externe des secrets, la supervision et les engagements de disponibilité ne sont pas réalisés.
- Les validations, identités, temps passés et signatures manquants ne sont pas inventés.
