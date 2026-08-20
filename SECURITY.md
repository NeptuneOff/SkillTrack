# Politique de sécurité

## Versions prises en charge

La branche par défaut et la dernière version démontrée sont les seules versions
maintenues. Les identifiants du compte de démonstration ne doivent jamais être
réutilisés dans un environnement public.

## Signaler une vulnérabilité

Ne publiez pas de secret, jeton ou donnée personnelle dans une issue publique.
Utilisez en priorité l'onglet **Security** du dépôt GitHub et un signalement privé.
Le rapport doit contenir :

- le composant et la version concernés ;
- les conditions de reproduction ;
- l'impact estimé ;
- une preuve de concept sans donnée réelle ;
- une proposition de correction, si elle existe.

Le mainteneur accuse réception, qualifie la criticité et prépare une correction
sur une branche dédiée. La publication détaillée attend que le correctif soit
disponible.

## Mesures attendues au déploiement

- remplacer `SECRET_KEY` et les mots de passe fournis pour la démonstration ;
- limiter les origines CORS au domaine réellement utilisé ;
- terminer TLS sur un reverse proxy de confiance ;
- conserver PostgreSQL hors d'Internet et sauvegarder la base ;
- appliquer les mises à jour Dependabot après passage de la CI ;
- consulter les alertes CodeQL et les journaux sans y stocker de données sensibles.
