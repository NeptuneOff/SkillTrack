# Guide utilisateur SkillTrack

## Se connecter

Ouvrez `http://localhost:5173`. Le compte de démonstration local est `demo@skilltrack.dev` avec le mot de passe `DemoPassword123!`. En cas d'identifiants refusés, un message est affiché ; vérifiez aussi que l'API est saine sur `http://localhost:8000/health`.

## Lire le dashboard

Le dashboard présente les données du compte connecté : nombre de séances, séries, volume calculé, intensité, évolution hebdomadaire, séances récentes et objectifs actifs triés par échéance. Une valeur n'est pas une recommandation médicale. Si l'historique est vide, commencez par une séance.

## Gérer une séance

1. Ouvrez **Séances**, puis **Nouvelle séance**.
2. Renseignez titre, date, type, intensité, durée et notes.
3. Pour chaque exercice, indiquez nom, catégorie, nombre de séries, répétitions, charge ou assistance, durée d'un maintien, difficulté et notes.
4. Utilisez **Ajouter un exercice** ou **Supprimer cet exercice** avant l'enregistrement.
5. Enregistrez ; le succès est confirmé et la liste est actualisée.
6. Depuis une carte, ouvrez le détail, modifiez ou supprimez. Une suppression définitive demande confirmation.

Une ligne d'exercice peut représenter plusieurs séries identiques via « nombre de séries ». Pour un maintien statique, les répétitions et la charge peuvent rester à zéro tandis que la durée est renseignée.

## Gérer un objectif

Dans **Objectifs**, définissez un skill, une description cible, une valeur actuelle, une valeur cible strictement positive, une unité, une priorité et éventuellement une échéance. Les actions permettent de modifier, terminer/rouvrir et supprimer. Le pourcentage est borné à 100 % à l'affichage ; la donnée actuelle peut continuer à progresser. Lors du premier passage à « terminé », l'environnement de développement envoie un message consultable sur MailHog (`http://localhost:8025`) ; une panne de ce service ne bloque pas l'objectif.

## Importer un CSV

1. Ouvrez **Import / Export** et téléchargez le modèle.
2. Conservez un fichier UTF-8 `.csv` de 2 Mo maximum.
3. Les colonnes `date`, `title` et `exercise` sont obligatoires.
4. Sélectionnez le fichier ; l'import affiche les lignes acceptées, rejetées et ignorées.
5. Corrigez les numéros de ligne signalés puis réimportez si nécessaire.
6. L'historique récent est affiché ; sa suppression n'efface pas les séances déjà créées.

Les lignes valides peuvent être importées même si d'autres lignes sont rejetées. Le format détaillé se trouve dans `docs/annexes/J_import_export.md`.

## Exporter ou effacer ses données

Dans **Import / Export**, téléchargez un CSV interopérable ou le JSON structuré de portabilité. Dans **Profil**, consultez l'identité du compte, exportez vos données ou demandez l'effacement. La suppression du compte et de ses données est définitive ; créez d'abord un export si nécessaire.

## Résoudre un problème courant

| Symptôme | Vérification |
|---|---|
| Page inaccessible | `docker compose ps`, puis santé API |
| Retour à la connexion | jeton absent/expiré ; reconnectez-vous |
| Erreur 422 | relire le champ et ses bornes affichées |
| Import refusé | extension, taille, UTF-8 et en-têtes requis |
| Bouton sans effet visible | attendre le feedback ; consulter console/log API puis déclarer un bug |
| Données inattendues | ne pas modifier ; conserver le contexte et vérifier le compte connecté |

Pour signaler une anomalie, fournir page, action, attendu/obtenu, heure, navigateur, commit et capture sans secret ni donnée personnelle. Le modèle d'analyse est dans `docs/annexes/R_doutes_bugs.md`.
