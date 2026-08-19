# ADR-0001 — Monolithe modulaire FastAPI

## Statut

Accepté pour le MVP.

## Contexte

SkillTrack doit rester simple à lancer et à auditer. Le besoin ne justifie pas une architecture microservices.

## Décision

Le backend est un monolithe modulaire : routes, services, repositories et modèles restent séparés.

## Conséquences

- Installation plus simple.
- Tests plus rapides.
- Migration possible vers des services séparés si un besoin réel apparaît.
- Nécessité de faire respecter les dépendances entre couches.
