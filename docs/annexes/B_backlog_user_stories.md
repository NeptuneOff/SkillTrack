# B — Backlog, critères et Definition of Done

## Règles de gestion du backlog

Priorité MoSCoW : **Must** indispensable à la démonstration, **Should** important mais contournable, **Could** amélioration. « Livré » ci-dessous signifie que l'implémentation et sa preuve technique existent sur la branche de travail ; une story n'est « terminée sur la release » que si son critère est démontrable et si toute la Definition of Done, dont PR/CI du commit final, est satisfaite.

| ID | Priorité | User story | Critères d'acceptation synthétiques | État au 19/08/2026 |
|---|---|---|---|---|
| US-01 | Must | En tant qu'utilisateur, je veux me connecter afin d'accéder à mes données | labels ; erreur lisible ; jeton stocké ; 401 gérée | Livré |
| US-02 | Must | Je veux comprendre l'état de ma progression | quatre métriques, huit semaines, objectifs actifs et séances récentes depuis la BDD | Livré et testé sur PostgreSQL |
| US-03 | Must | Je veux lister et consulter mes séances | état vide/chargement/erreur ; données triées | Livré |
| US-04 | Must | Je veux créer une séance avec un exercice | champs guidés ; bornes ; persistance ; confirmation | Livré |
| US-05 | Must | Je veux modifier puis supprimer ma séance | formulaire prérempli ; confirmation destructive ; absence après suppression | Livré |
| US-06 | Must | Je veux ajouter et retirer des exercices avant enregistrement | une ligne minimum ; boutons explicites | Livré |
| US-07 | Must | Je veux gérer une cible mesurable | créer, modifier, terminer/rouvrir et supprimer | Livré |
| US-08 | Must | Je veux importer mon historique CSV | exemple, format, limite, lignes rejetées détaillées | Livré |
| US-09 | Must | Je veux récupérer toutes mes données | CSV interopérable + JSON structuré, propriétaire uniquement | Livré ; contenu/round-trip automatisés et téléchargements E2E |
| US-10 | Must | Je veux effacer mon compte | confirmation explicite ; suppression en cascade | Livré et testé sur PostgreSQL |
| US-11 | Must | En tant que jury, je veux lancer le projet sans assistance | README, Compose, compte démo, healthchecks | Livré ; recette machine vierge requise |
| US-12 | Should | En tant qu'utilisateur au clavier, je veux parcourir l'app | lien d'évitement, ordre de tabulation, focus visible et navigation | Livré ; parcours Chromium vert, session lecteur d'écran recommandée |
| US-13 | Should | En tant que mainteneur, je veux une livraison contrôlée | CI, runbook, sauvegarde/restauration et preuves | Livré localement ; statut CI à rattacher au commit final |
| US-14 | Could | Je veux recevoir une notification par e-mail | message visible dans MailHog, panne SMTP non bloquante | Livré en développement et testé |

## Definition of Ready (DoR)

Une story est prête lorsque :

- l'utilisateur, le besoin et la valeur sont formulés ;
- critères positifs, négatifs et droits d'accès sont définis ;
- données d'entrée/sortie et dépendances sont identifiées ;
- impact sécurité, RGPD, accessibilité et migration est examiné ;
- la story est estimable et sa priorité arbitrée.

## Definition of Done (DoD)

- comportement conforme aux critères et test manuel effectué ;
- tests automatisés pertinents ajoutés ou justification écrite ;
- Ruff/mypy/pytest et ESLint/Vitest/build réussissent ;
- filtrage `owner_id` vérifié pour toute donnée utilisateur ;
- erreurs, chargements et états vides présents dans l'interface ;
- contrats CSV/JSON et documentation actualisés en cas de changement ;
- aucune donnée secrète ou artefact personnel ajouté à Git ;
- PR relue et CI verte avant fusion ;
- preuve datée conservée pour une release jury.

## Backlog de fermeture RNCP

| Action | Bloc concerné | Critère de fermeture | Responsable/validation |
|---|---|---|---|
| Maintenir audit clavier + axe navigateur | BC01-C7 | 0 violation/incomplet, reflow sans débordement | test Playwright vert ; testeur lecteur d'écran conseillé |
| Faire une recette sur machine vierge | BC02-C9/C11, BC04-C5 | commandes, captures et PV | Karl + valideur tiers |
| Conserver le test de deux propriétaires | BC01-C4/C10, BC04-C3 | accès croisé refusé et exports étanches | test automatisé vert |
| Faire relire architecture et risques | BC02-C6/C10/C12 | compte rendu de revue et décisions | pair/formateur |
| Mener une démonstration utilisateur | BC02-C10 | feedback, incompréhensions et actions | utilisateur pilote |
| Documenter une situation d'entreprise authentique | BC02-C1 à C3 | procédure/AS-IS/TO-BE/flux validés | référent réel |

## Traçabilité

Le présent backlog est une reconstruction documentaire datée : aucun sprint historique ni temps passé n'a été inventé. Les dates et commits vérifiables sont consignés dans `C_planning.md` et `O_git_tracabilite.md`.
