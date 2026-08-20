# Journal des changements

Ce fichier suit les principes de *Keep a Changelog*. Les versions ne sont
considérées comme publiées qu'après création effective d'un tag Git.

## Non publié

### Ajouté

- matrice de preuves alignée sur les 36 compétences officielles RNCP36463 ;
- preuves reproductibles de performance, sauvegarde et restauration ;
- environnement Docker de production, CodeQL et Dependabot ;
- tests fonctionnels renforcés et scénario de recette jury.

### Corrigé

- sérialisation et exhaustivité des exports personnels ;
- atomicité et rapport d'erreurs de l'import CSV ;
- intégrité des relations utilisateur sur les volumes PostgreSQL existants ;
- calcul du nombre réel de séries ;
- accessibilité et gestion des erreurs de l'interface.

### Sécurité

- contraintes de données, en-têtes HTTP et journalisation sans contenu sensible ;
- procédure de sauvegarde avant migration et politique de signalement.
