# H-RSE-01 — Mesures RSE et écoconception

## Baseline et seuils

| Indicateur | Baseline à mesurer | Objectif |
|---|---:|---:|
| Poids du dashboard chargé | à mesurer | -20 % après optimisation si > 500 Ko |
| Nombre de requêtes initiales | à mesurer | ≤ 10 requêtes utiles |
| Temps médian de chargement local | à mesurer | < 1,5 s |
| Taille image backend | à mesurer | image slim, dépendances minimales |

## Décisions RSE

- Pas de polling temps réel permanent dans le MVP.
- Pagination ou limitation des historiques volumineux.
- Export à la demande.
- Images Docker slim.
- Dépendances vérifiées et limitées.
