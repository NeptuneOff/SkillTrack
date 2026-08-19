# Q — Capacité et performance

## 1. Hypothèse de dimensionnement

SkillTrack est un MVP local sans trafic réel. La cible de test retenue n'est pas une promesse de production : **20 utilisateurs simultanés**, 200 consultations authentifiées du dashboard, sur la machine locale du test. Environnement mesuré : Windows 11, Python 3.14.6, 16 processeurs logiques, API sur `localhost`. La volumétrie BDD et la RAM/CPU consommées n'ont pas encore été capturées.

Pour un service public, il faudrait mesurer les utilisateurs actifs, fréquence des saisies, taille moyenne d'une séance et rétention afin de calculer stockage, connexions et capacité. Ces informations ne sont pas disponibles dans ce projet pédagogique.

## 2. Protocole automatisé

Le script `scripts/performance_test.py` :

1. vérifie l'API et obtient un jeton ;
2. lance des requêtes concurrentes sur `/dashboard` ;
3. mesure latences, succès/échecs et débit ;
4. compare le p95 au seuil ;
5. écrit un JSON dans `artifacts/performance/` sans jeton ni donnée personnelle.

Commande indicative après démarrage de Compose :

```powershell
python scripts/performance_test.py
```

## 3. Résultat final de la release candidate du 19/08/2026

| Paramètre/mesure | Valeur |
|---|---:|
| Utilisateurs concurrents simulés | 20 |
| Requêtes dashboard | 200 |
| Succès | 100 % |
| p95 | 128,05 ms |
| médiane / p99 / maximum | 103,81 / 143,92 / 153,41 ms |
| Débit | 186,53 requêtes/s |
| Seuil p95 | 1 000 ms |
| Verdict | conforme aux deux seuils |

Source versionnable ultime : `artifacts/performance/2026-08-19-verify-final.json`, avec les mêmes données que le résultat `latest.json` produit par le dernier `scripts/verify.ps1` après le rebuild et le remplacement de Passlib par bcrypt direct. Les fichiers antérieurs sont conservés comme historique, mais une comparaison de tendance exige le même commit, le même dataset et la même machine.

## 4. Analyse de capacité

Le test montre qu'une consultation simple respecte le seuil dans ce contexte. Il ne couvre pas : login en rafale, écritures concurrentes, verrouillage BDD, import/export volumineux, endurance, montée progressive, CPU/RAM ou réseau distant. Le dashboard charge les objets puis agrège en Python ; son coût croît avec l'historique du propriétaire.

## 5. Plan de tests suivant

- consigner CPU, RAM, versions, nombre de séances/exercices et taille BDD ;
- mesurer p50/p95/p99 et erreurs sur login, dashboard, création et export ;
- paliers 20/50/100 utilisateurs, puis test d'endurance 30 minutes ;
- dataset synthétique de 10 000 séances / 60 000 exercices ;
- expliquer le premier goulet : connexions, requête, sérialisation ou frontend ;
- comparer avant/après optimisation sans changer l'environnement.

Critères proposés : erreurs < 1 %, p95 lecture < 1 000 ms dans l'environnement de jury, aucune fuite de connexion et aucun mélange de données.
