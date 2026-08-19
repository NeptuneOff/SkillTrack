# A-01 — Cahier des charges fonctionnel

## Besoin

SkillTrack répond au besoin d'un pratiquant de calisthénie qui souhaite suivre ses séances, ses skills, ses variantes et ses progressions sans dépendre d'un tableur dispersé.

## Objectifs mesurables du MVP

- Créer un compte et se connecter.
- Créer, lire, modifier et supprimer ses propres séances.
- Enregistrer exercices, séries, répétitions, charge externe, temps de maintien et RPE.
- Importer un CSV structuré avec rapport d'erreurs.
- Exporter ses données en CSV et JSON.
- Consulter un volume hebdomadaire par exercice.
- Bloquer l'accès aux données d'un autre utilisateur.
- Lancer le projet depuis Docker en moins de 10 minutes sur environnement vierge.

## Hors périmètre MVP

- Coaching individualisé.
- Recommandations automatiques de progression.
- Application mobile native.
- Données de santé sensibles.

## Critères d'acceptation

| ID | Exigence | Critère |
|---|---|---|
| EX-01 | Connexion sécurisée | JWT obtenu après identifiants valides uniquement |
| EX-02 | Isolation utilisateur | un utilisateur ne peut pas lire une séance d'un autre utilisateur |
| EX-03 | Import CSV | rapport précis des lignes acceptées et rejetées |
| EX-04 | Export | fichier limité aux données du propriétaire |
| EX-05 | Stats | volume hebdomadaire exact sur jeu de test |
| EX-06 | Installation | `docker compose up --build` démarre frontend/API/BDD |
