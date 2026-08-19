# R — Doutes techniques, bugs et analyses de causes

## 1. Registre synthétique

| ID | Symptôme | Cause racine | Correction/preuve | Statut |
|---|---|---|---|---|
| BUG-01 | quitter « Séances » vers Objectifs ou une autre page donnait un fond vide sans menu | l'effet React retournait indirectement une Promise ; React utilisait ce retour comme fonction de nettoyage | effet encapsulé sans retour Promise, `PageErrorBoundary`, test navigation `app.test.jsx` | Corrigé/testé |
| BUG-02 | CI frontend échouait avec `markAsUncloneable is not a function` | dépendances jsdom/undici récentes incompatibles avec Node 20 | CI passée à Node 22, alignée sur Dockerfile | Corrigé/CI verte avant nouveau lot |
| BUG-03 | CI backend : `relation "users" does not exist` | `TestClient(app)` global n'activait pas le cycle startup sur base PostgreSQL vierge | fixture context manager module ; startup exécuté | Corrigé/testé |
| BUG-04 | configuration CI non prise en compte | noms `JWT_SECRET`/`CORS_ORIGINS` différents des champs attendus | `SECRET_KEY`/`BACKEND_CORS_ORIGINS` | Corrigé |
| BUG-05 | avertissement de compatibilité Passlib/bcrypt et risque de troncature >72 octets | couche Passlib obsolète et limite bcrypt non exposée dans le contrat | Passlib supprimé, bcrypt direct 5.0.0, anciens hashes compatibles, validation 72 octets et test HTTP 422 | Corrigé/testé |
| BUG-06 | e-mail démo `.local` rejeté | validation standard de l'adresse | compte passé à `demo@skilltrack.dev` | Corrigé |
| BUG-07 | export JSON contenait des représentations d'objets et seulement des données de dashboard | réutilisation d'un DTO destiné à l'écran plutôt qu'un contrat de portabilité | `data_exchange.py`, schéma versionné et tests profil/séances/objectifs/imports | Corrigé/testé |
| BUG-08 | nombre de « séries » égal au nombre de lignes d'exercice | agrégation avec `len(w.sets)` au lieu de la somme `set_count` | somme réelle et test avec 3 + 2 séries | Corrigé/testé |
| BUG-09 | des données démo supprimées pouvaient revenir au redémarrage | seed déclenché lorsque le compteur de séances passait sous un seuil | seed exécuté uniquement lors de la création du compte démo | Corrigé/testé |
| BUG-10 | audit navigateur : overflow CSV puis table historique à 320 px, ARIA invalide et contrastes axe indéterminés | largeurs minimales/conteneurs non réductibles, attributs mal portés et surfaces en dégradé | containment/table corrigés, surfaces déterministes, attente des loaders ; axe 0 violation/incomplet et reflow 5/5 | Corrigé/testé |

## 2. Analyse détaillée BUG-01

- **Reproduction :** connexion → Séances → Objectifs (ou autre menu).
- **Observé :** disparition de toute l'application, fond seul.
- **Hypothèse :** erreur au démontage du composant Séances.
- **Cause :** une fonction asynchrone appelée directement depuis `useEffect` était retournée comme cleanup ; React attend `undefined` ou une fonction.
- **Correction :** `useEffect(() => { load(); }, [])` et frontière d'erreur de page.
- **Non-régression :** le test rend la vraie `App`, ouvre Séances, puis Objectifs, et vérifie le titre ainsi que le bouton Dashboard.
- **Amélioration :** conserver un gestionnaire global de rejet et tester chaque transition de menu.

## 3. Analyse détaillée BUG-02/03

Les vérifications locales passaient, mais l'environnement distant différait : Node 20 contre dépendances demandant Node 22, et PostgreSQL CI vierge contre base locale déjà initialisée. La leçon n'est pas seulement « changer une version » : aligner les runtimes, tester le lifecycle de l'application et vérifier sur base vierge.

## 4. Trame pour toute nouvelle anomalie

```text
ID / sévérité / date / commit
Environnement et données anonymisées
Étapes minimales de reproduction
Attendu / observé / message exact
Hypothèses testées et résultats
Cause racine (pas seulement symptôme)
Correction et risques
Test de non-régression
Commit, PR et résultat CI
```

La release finale doit conserver le lien entre ce registre, le diff, les tests et le résultat CI. Une correction n'est close que si son test échoue sur l'ancien comportement et passe sur le nouveau ou si la reproduction avant/après est archivée.
