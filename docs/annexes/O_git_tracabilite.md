# O — Git, décisions et traçabilité

## 1. Historique vérifiable au 19/08/2026

| Commit | Date locale | Objet | Lecture RNCP |
|---|---|---|---|
| `d0ca5b5` | 19/08/2026 09:10 | structure initiale SkillTrack | état de départ et documentation initiale |
| `8492e3d` | 19/08/2026 21:25 | refonte pour démonstration RNCP | incrément fonctionnel principal |
| `3fc87e0` | 19/08/2026 21:33 | correction environnements CI | diagnostic et correction de livraison |
| `950c41b` | 19/08/2026 22:54 | fiabilisation backend et échanges de données | migrations, sécurité, import/export, isolation et tests PostgreSQL |
| `ce54773` | 19/08/2026 22:54 | fiabilisation interface et parcours jury | composants réels, accessibilité, navigation et E2E Chromium |
| `1201985` | 19/08/2026 22:54 | durcissement livraison et recette | Compose dev/prod, CI, scripts, sauvegarde, smoke et performance |
| `8e2e48d` | 19/08/2026 23:01 | correction des alertes CodeQL de l'import | rapport CSV sans texte brut d'exception et non-régression CSP sans faux positif |

Branche de travail : `agent/rncp-ready-skilltrack`. Pull request : GitHub `NeptuneOff/SkillTrack#1`, créée en brouillon afin de ne pas fusionner avant contrôle. Au moment de cette preuve, `main` pointe encore sur l'état initial ; vérifier à nouveau avant la soutenance.

## 2. Convention à appliquer

- une branche courte par lot : `feat/...`, `fix/...`, `docs/...` ;
- commit impératif, descriptif et borné ;
- PR avec contexte, changements, tests, risques, captures et checklist ;
- aucune fusion avec CI rouge ou réserve bloquante ;
- tag annoté uniquement après recette : `v1.0.0-rncp` par exemple ;
- relier bug, test de non-régression, commit et preuve CI.

## 3. Checklist de PR

- [ ] périmètre et hors-périmètre compris ;
- [ ] diff relu, aucun secret/dump/build ajouté ;
- [ ] tests et documentation mis à jour ;
- [ ] migrations et rollback évalués ;
- [ ] impacts sécurité/RGPD/RGAA/RSE examinés ;
- [ ] CI entièrement verte ;
- [ ] revue humaine et remarques traitées ;
- [ ] recette/Go-No-Go pour une release.

## 4. Preuves à exporter

Pour le dossier final : graphe Git avec dates, PR et diff, résultat CI du commit fusionné, commentaire de revue d'un pair, tag de release, et lien entre les anomalies de `R_doutes_bugs.md` et leurs tests. Les échanges avec un assistant ne remplacent pas une revue professionnelle externe.

## 5. Limite

L'historique comporte un gros commit de refonte initial, moins lisible qu'une suite d'incréments. Les corrections finales ont ensuite été séparées en lots backend, frontend, livraison, preuves RNCP et sécurité CI. Le commit documentaire qui contient cette annexe est identifiable par son objet et par la PR ; son propre hash ne peut pas être inscrit dans son contenu sans créer une référence circulaire.
