# Contribuer à SkillTrack

## Flux Git

1. Partir de la branche par défaut à jour.
2. Créer une branche courte `feature/...`, `fix/...` ou `docs/...`.
3. Faire des commits ciblés dont le message explique le résultat.
4. Ouvrir une pull request décrivant le besoin, la cause et les vérifications.
5. Attendre la réussite de la CI et une relecture avant fusion.

## Définition de terminé

Une évolution fonctionnelle n'est terminée que si :

- le comportement nominal et les erreurs sont traités ;
- les entrées sont validées côté interface et côté API ;
- les données restent isolées par utilisateur ;
- les parcours clavier et les noms accessibles sont vérifiés ;
- un test pertinent échoue avant la correction puis réussit après ;
- la documentation et la matrice RNCP sont mises à jour ;
- aucun secret ni donnée personnelle n'est ajouté à Git ;
- `scripts/verify.ps1` ou `scripts/verify.sh` réussit.

## Relecture

La relecture vérifie en priorité la sécurité, les migrations de données, la
compatibilité import/export, les suppressions RGPD et les actions destructives.
Une migration ou une restauration doit disposer d'une sauvegarde vérifiée et
d'un plan de retour arrière.

Les retours sont formulés sur le comportement ou le code, avec une proposition
actionnable. Toute décision structurante est consignée dans la documentation
d'architecture ou le journal de projet.
