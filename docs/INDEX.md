# Index du portefeuille de preuves SkillTrack

Point d'entrée jury : [`rncp/MATRICE_COMPETENCES_RNCP.md`](rncp/MATRICE_COMPETENCES_RNCP.md). La matrice suit les 36 compétences officielles 10/13/8/5 et renvoie aux livrables ci-dessous.

## Cadrage et conception

| Preuve | Contenu |
|---|---|
| [`annexes/A_cahier_des_charges.md`](annexes/A_cahier_des_charges.md) | besoin, périmètre, exigences et checklist |
| [`annexes/B_backlog_user_stories.md`](annexes/B_backlog_user_stories.md) | backlog, DoR/DoD et fermeture RNCP |
| [`annexes/D_architecture.md`](annexes/D_architecture.md) | contexte, couches, ADR, réutilisation et MailHog |
| [`annexes/E_mcd_mpd.md`](annexes/E_mcd_mpd.md) | MCD, MPD, dictionnaire, contraintes et migrations |
| [`DIRECTION_ARTISTIQUE.md`](DIRECTION_ARTISTIQUE.md) | principes UI/UX Nocturne Kinetic |

## Sécurité, responsabilité et qualité

| Preuve | Contenu |
|---|---|
| [`annexes/F_securite.md`](annexes/F_securite.md) | risques, criticité, contrôles et traitement |
| [`annexes/H_RGPD.md`](annexes/H_RGPD.md) | registre, droits, minimisation et agrégats |
| [`annexes/H_RGAA.md`](annexes/H_RGAA.md) | audit axe navigateur, clavier/reflow et limite lecteur d'écran |
| [`annexes/H_RSE.md`](annexes/H_RSE.md) | écoconception, indicateurs et actions |
| [`annexes/I_tests_recette.md`](annexes/I_tests_recette.md) | stratégie, jeux d'essai, recette et PV |
| [`annexes/Q_performance.md`](annexes/Q_performance.md) | benchmark, capacité et limites |

## DevOps, échange et maintenance

| Preuve | Contenu |
|---|---|
| [`annexes/J_import_export.md`](annexes/J_import_export.md) | mapping, formats, erreurs et round-trip |
| [`annexes/K_ITIL_deploiement.md`](annexes/K_ITIL_deploiement.md) | Go/No-Go, sauvegarde, rollback et diagnostic |
| [`annexes/L_extraits_code.md`](annexes/L_extraits_code.md) | guide des symboles à présenter |
| [`annexes/O_git_tracabilite.md`](annexes/O_git_tracabilite.md) | commits, PR et checklist de revue |
| [`annexes/R_doutes_bugs.md`](annexes/R_doutes_bugs.md) | incidents, causes racines et non-régressions |
| [`annexes/S_algorithmes.md`](annexes/S_algorithmes.md) | volume, agrégats, import et sérialisation |
| [`annexes/U_retrodocumentation.md`](annexes/U_retrodocumentation.md) | analyse organique et évolution de l'existant |

## Pilotage et communication

| Preuve | Contenu |
|---|---|
| [`annexes/C_planning.md`](annexes/C_planning.md) | jalons vérifiables, estimations et disponibilité |
| [`annexes/P_processus_et_flux.md`](annexes/P_processus_et_flux.md) | procédures, AS-IS/TO-BE, flux et RACI |
| [`annexes/T_collaboration.md`](annexes/T_collaboration.md) | protocoles de revue, présentation et inclusion |
| [`GUIDE_UTILISATEUR.md`](GUIDE_UTILISATEUR.md) | parcours autonome et aide |

## Preuves d'exécution versionnées

| Preuve | Résultat archivé |
|---|---|
| [Playwright jury + accessibilité](../artifacts/accessibility/2026-08-19-playwright.md) | 2/2 scénarios Chromium, axe/clavier/reflow et parcours jury |
| [Audit navigateur détaillé](../artifacts/accessibility/2026-08-19-browser-audit.md) | règles axe par vue, écarts détectés puis corrigés |
| [`annexes/V_captures_interface.md`](annexes/V_captures_interface.md) | index P01–P32 des vues et interactions réelles, avec distinction entre preuve d’interface et validation technique |
| [Benchmark du verify final](../artifacts/performance/2026-08-20-rncp-captures-final.json) | 200/200, p95 et environnement machine |
| [Sauvegarde/restauration](../artifacts/operations/2026-08-19-backup-restore.md) | dump restauré dans une base temporaire puis contrôlé |
| [Smoke de la stack production](../artifacts/operations/2026-08-19-production-smoke.md) | images, migrations, proxy, JWT et nettoyage isolé |

## Fermeture avant soutenance

1. Exécuter [`rncp/CONTROLE_FINAL.md`](rncp/CONTROLE_FINAL.md) sur le commit présenté et intégrer ces preuves au dossier officiel d'au moins 60 pages.
2. Joindre les sorties CI/verify/E2E/performance et les captures anonymisées.
3. Conserver l'audit axe/clavier/reflow daté et faire réaliser la session lecteur d'écran humaine recommandée.
4. Ajouter les preuves authentiques de processus d'entreprise, collaboration, décision collective, disponibilité, démonstration et recette signée.
5. Mettre à jour les statuts de la matrice uniquement après vérification des pièces.
