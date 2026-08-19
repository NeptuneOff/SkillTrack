# ADR-0002 — Service SMTP de test MailHog

## Statut

Accepté pour le MVP pédagogique.

## Contexte

Le référentiel demande de démontrer l'intégration d'éléments logiciels hétérogènes. SkillTrack doit intégrer au moins un service externe/local réutilisé sans dépendre d'un fournisseur payant.

## Décision

MailHog est utilisé comme service SMTP local. Le backend envoie un email de bienvenue après inscription. En développement, l'email est visible sur http://localhost:8025.

## Conséquences

- Intégration testable sans données réelles.
- Pas de coût ni de secret fournisseur.
- Preuve claire : code `EmailService`, service Docker `mailhog`, capture de l'email reçu, test d'intégration possible.
