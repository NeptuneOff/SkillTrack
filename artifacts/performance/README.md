# Preuves de performance

Les fichiers JSON de ce dossier sont produits par `scripts/performance_test.py`.
Ils contiennent le scénario, l'environnement, les seuils et les mesures brutes
nécessaires pour reproduire et commenter un test de charge devant le jury.

Commande de référence :

```powershell
python scripts/performance_test.py --users 20 --requests 200 --warmup 5 `
  --output artifacts/performance/latest.json
```

Seuils par défaut :

- au moins 99 % de réponses HTTP 200 ;
- latence p95 inférieure ou égale à 1 000 ms.

Ces mesures portent sur une machine locale et sur une charge de lecture du
dashboard. Elles constituent une preuve de protocole et un point de comparaison,
pas un engagement de capacité pour une infrastructure de production.
