# Contrôle final obligatoire avant démonstration

## Règle

Exécuter cette grille sur le **commit exact présenté**, après reconstruction des images. `✅` signifie preuve disponible et vérifiée ; `🟠` signifie contrôle final ou preuve humaine requis ; `❌` signifie bloquant. Ne pas transformer automatiquement `🟠` en `✅` après une modification de code.

| # | Contrôle demandé | Preuve de sortie | État documentaire au 19/08/2026 |
|---|---|---|---|
| 1 | Utilisable sans explication orale | test utilisateur + parcours README | 🟠 test externe requis |
| 2 | Toutes les pages visibles ont une vraie interface | connexion/dashboard/séances/objectifs/import/profil | ✅ six vues contrôlées par Vitest/axe et Playwright |
| 3 | Boutons actifs fonctionnels ou clairement désactivés | parcours manuel de chaque action | 🟠 recette finale |
| 4 | Formulaires : labels, aides, placeholders, validations | audit DOM + erreurs API | ✅ composants réels, axe Chromium 0 violation/incomplet et validations API ; recette humaine recommandée |
| 5 | Dashboard sur vraies données | PostgreSQL + chiffres attendus | ✅ agrégats, séries réelles et objectifs actifs testés sur PostgreSQL |
| 6 | Séances créables/modifiables/supprimables | API, UI et tests | ✅ |
| 7 | Exercices ajoutables/supprimables | vrai composant et test | ✅ API, vrai composant frontend et parcours Playwright verts |
| 8 | Objectifs cycle complet | UI/API/test CRUD | ✅ |
| 9 | Import CSV + rapport d'erreur | cas valide/invalide et historique | ✅ |
| 10 | Exports CSV/JSON | tests de contenu exact, round-trip et fichiers téléchargés | ✅ backend exhaustif/round-trip et téléchargements Playwright verts |
| 11 | Authentification JWT | login, expiration/absence et routes protégées | ✅ JWT expirant configuré ; jetons absents/invalides et mauvais identifiants testés |
| 12 | Filtrage par utilisateur | test croisé A/B, CRUD, imports, dashboard et exports | ✅ test PostgreSQL dédié vert |
| 13 | PostgreSQL réellement utilisé | service, psycopg, données persistantes | ✅ |
| 14 | Docker Compose fonctionne | services healthy après rebuild | ✅ stack dev et simulation production isolée validées ; répéter sur machine jury |
| 15 | README permet un lancement autonome | clone/machine vierge sans assistance | 🟠 test externe/machine vierge requis |
| 16 | Tests couvrent fonctions principales | matrice `I_tests_recette.md`, CI | ✅ backend 20/20 à 92,36 %, frontend 10/10, E2E jury + accessibilité ; recette humaine distincte |
| 17 | Documentation RNCP existe | annexes et matrice | ✅ |
| 18 | Matrice indique les preuves par compétence | 36 lignes, 10/13/8/5, chemins/statuts | ✅ |
| 19 | Matière pour défendre les 4 blocs | portfolio + preuves externes | 🟠 technique solide ; BC02 externe incomplet |
| 20 | Limites restantes signalées honnêtement | README, matrice et annexes | ✅ |

## Procédure technique

```powershell
git status --short
git rev-parse HEAD
Copy-Item .env.example .env -ErrorAction SilentlyContinue
docker compose up --build -d
docker compose ps
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify.ps1
python scripts/performance_test.py
```

Puis exécuter REC-01 à REC-12 de `docs/annexes/I_tests_recette.md`, remplir le PV, joindre les rapports RGAA et performance et vérifier que les fichiers exportés ne contiennent aucune donnée inattendue.

## Go/No-Go jury

No-Go si l'un des éléments suivants apparaît : écran vide/navigation cassée, données d'un tiers accessibles, export incomplet/non parsable, perte BDD, échec auth/CRUD/import, service non sain, test/CI rouge ou migration sans retour arrière.

Go technique lorsque tous les contrôles automatisés et REC critiques sont verts. Go RNCP complet uniquement lorsque les preuves externes annoncées dans la matrice (cas d'entreprise, collaboration, validations et PV) ont été réellement jointes.

## Preuves à archiver

- commit/tag, URL de PR et CI ;
- sortie `verify`, `docker compose ps` et benchmark ;
- captures des parcours, Swagger et rapports import/export ;
- rapport accessibilité ;
- journal de sauvegarde/restauration sans dump ;
- comptes rendus anonymisés, feedback et PV signés.
