# S — Analyse des algorithmes métier

## 1. Calcul de volume

Entrée : une séance et ses lignes d'exercice. Pour chaque ligne :

```text
charge_effective = max(charge_kg - assistance_kg, 1)
contribution = nombre_series × (répétitions × charge_effective + durée_secondes × 0,2)
volume_séance = somme(contribution)
```

Implémentation : `backend/app/services.py:workout_volume`. Le plancher à 1 permet de compter un exercice au poids du corps mais ne représente pas la masse réelle du sportif. Le coefficient `0,2` pour les maintiens est une convention du MVP, à faire valider comme règle métier.

Cas à tester : zéro répétition avec durée, assistance supérieure à charge, plusieurs séries, valeurs maximales, séance vide héritée et arrondi.

Complexité : O(S) pour S lignes dans la séance, mémoire O(1).

## 2. Agrégation dashboard

```text
charger séances du propriétaire avec exercices
total_volume = somme(volume_séance)
total_séries = somme(set_count)
pour chacune des 8 semaines : sommer les séances dont la date est dans l'intervalle
calculer variation semaine courante / précédente si précédente > 0
charger uniquement les objectifs status=actif, triés par échéance puis nom
```

Implémentation : `services.py:dashboard`. Le filtre d'objectifs actifs évite de présenter les objectifs terminés/archivés comme prochaine action. Dans sa forme en mémoire, la construction hebdomadaire est O(8×W×S) au pire. Huit étant constant, elle reste O(W×S), mais la quantité chargée croît avec l'historique. Alternative future : agrégation SQL par semaine, index `(owner_id,date)` et pagination.

## 3. Import CSV

Décomposition :

```text
lire au plus 2 000 001 octets
→ refuser >2 Mo
→ décoder UTF-8-sig
→ distinguer format legacy (en-têtes date/title/exercise) et export complet (record_type)
→ pour chaque ligne : convertir + valider
→ indexer par workout_id ou (date,title) dans un dictionnaire
→ ajouter l'exercice au groupe ou consigner Ligne N: erreur
→ créer les séances valides
→ enregistrer le rapport d'import
```

Complexité : O(N) temps et O(N) mémoire dans le pire cas. Le dictionnaire évite une recherche quadratique des séances. La route construit le plan et tous les objets avant un commit unique ; toute exception SQLAlchemy déclenche un rollback global, vérifié par un test de panne forcée.

## 4. Sérialisation des exports

Le besoin diffère du dashboard : l'export parcourt toutes les entités du propriétaire, les convertit en primitives JSON/CSV et préserve la structure. `build_json_export` produit le document canonique ; `build_csv_export` le transforme en enregistrements typés et neutralise les formules tableur. Tests invariants : JSON parsable, listes exhaustives, aucun secret, aucun objet d'un autre propriétaire et réimport cohérent.

## 5. Évolution sans régression

Pour toute modification : figer un jeu d'entrée/sortie actuel, écrire le cas qui échoue, modifier une règle à la fois, exécuter anciens et nouveaux tests, comparer résultats et performance, puis faire valider la nouvelle règle métier. L'évolution du compteur de séries (`len` → somme de `set_count`) est prouvée par `test_dashboard_uses_real_set_count_and_volume` ; l'ancien calcul aurait retourné 2 au lieu de 5.
