# Q — Protocole de performance

## Hypothèses

- 500 utilisateurs inscrits.
- 50 utilisateurs simultanés en consultation.
- Dataset de test : 10 000 séances, 60 000 séries.

## Scénarios

- Login.
- Consultation dashboard.
- Création séance.
- Export JSON.

## Mesures

- p50/p95.
- taux d'erreur.
- CPU/RAM.
- connexions BDD.
- taille dataset.

## Critères

- p95 < 500 ms sur consultation simple en environnement local contrôlé.
- erreurs < 1 %.
