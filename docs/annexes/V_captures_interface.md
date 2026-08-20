# Annexe V — Captures de l’interface et parcours démontrés

## 1. Objet et périmètre

Cette annexe indexe les **32 captures d’écran P01 à P32**, réalisées le 20 août 2026 dans l’interface web de SkillTrack. Le lot couvre la connexion, le dashboard, la navigation, le cycle de vie des séances et des objectifs, l’import/export ainsi que les fonctions de profil et de protection des données.

Les images montrent uniquement l’application dans le navigateur : aucune console Docker, commande Git, page Swagger ou sortie de tests n’est utilisée comme capture fonctionnelle.

## 2. Règle de lecture des preuves

Deux niveaux de preuve doivent rester distincts :

- **preuve d’interface** : la capture atteste qu’une vue, un formulaire, un état, une confirmation ou un retour utilisateur est réellement affiché après le parcours indiqué ;
- **validation technique** : les tests automatisés, contrôles API, vérifications PostgreSQL, scénarios multi-utilisateur et analyses d’accessibilité démontrent séparément le traitement, la persistance, l’isolation, le contenu des fichiers et les propriétés non visibles à l’écran.

Une image de succès ne suffit donc pas, à elle seule, à prouver l’intégrité d’une transaction, la validité complète d’un fichier téléchargé, l’expiration d’un JWT ou l’absence d’accès croisé entre utilisateurs. Les preuves techniques associées restent celles de la matrice RNCP, de l’annexe de recette et des rapports d’exécution versionnés.

## 3. Catalogue des captures

### 3.1 Connexion, dashboard et navigation

| ID | Fonction prouvée dans l’interface | Interaction réelle permettant d’atteindre l’état | Compétences RNCP principalement reliées | Image |
|---|---|---|---|---|
| P01 | Page de connexion complète : champs e-mail et mot de passe, libellés, aide et compte de démonstration | Ouverture de la route publique sans session active | BC01-C1, BC01-C2, BC01-C7 | [`P01_page_connexion.png`](../../artifacts/rncp/screenshots/P01_page_connexion.png) |
| P02 | Dashboard authentifié avec indicateurs, dernière activité, objectifs actifs et progression récente | Saisie des identifiants puis validation du formulaire de connexion | BC01-C1, BC01-C2, BC01-C7, BC04-C3 | [`P02_dashboard_apres_connexion.png`](../../artifacts/rncp/screenshots/P02_dashboard_apres_connexion.png) |
| P03 | Navigation générale et repère visuel de la section active | Parcours par les liens Dashboard, Séances, Objectifs, Import/Export et Profil | BC01-C1, BC01-C2, BC01-C7 | [`P03_navigation_generale.png`](../../artifacts/rncp/screenshots/P03_navigation_generale.png) |
| P04 | Cartes statistiques détaillées calculées à partir des données du compte | Consultation du dashboard authentifié alimenté par les données de démonstration | BC01-C2, BC01-C7, BC04-C3 | [`P04_dashboard_stats_detaillees.png`](../../artifacts/rncp/screenshots/P04_dashboard_stats_detaillees.png) |

### 3.2 Séances et exercices

| ID | Fonction prouvée dans l’interface | Interaction réelle permettant d’atteindre l’état | Compétences RNCP principalement reliées | Image |
|---|---|---|---|---|
| P05 | Liste non vide des séances avec résumé et actions consulter, modifier, supprimer et ajouter | Clic sur « Séances » et chargement de la liste du compte connecté | BC01-C1, BC01-C2, BC01-C7, BC03-C7 | [`P05_page_seances_liste.png`](../../artifacts/rncp/screenshots/P05_page_seances_liste.png) |
| P06 | Formulaire de création d’une séance sans données métier saisies, avec libellés, aides et valeurs par défaut attendues | Ouverture de la page Séances : seuls la date et les paramètres usuels sont préinitialisés | BC01-C1, BC01-C2, BC01-C7, BC03-C7 | [`P06_formulaire_creation_seance_vide.png`](../../artifacts/rncp/screenshots/P06_formulaire_creation_seance_vide.png) |
| P07 | Formulaire de séance renseigné avec un cas d’usage réaliste | Saisie des informations de la séance dans les champs contrôlés | BC01-C1, BC01-C2, BC03-C7 | [`P07_formulaire_creation_seance_rempli.png`](../../artifacts/rncp/screenshots/P07_formulaire_creation_seance_rempli.png) |
| P08 | Ajout d’un exercice et disponibilité de ses attributs métier | Clic sur « Ajouter un exercice », puis saisie du nom, de la catégorie, de la charge, de l’assistance, du RPE et des notes | BC01-C1, BC01-C2, BC01-C7, BC03-C7 | [`P08_ajout_exercice_dans_seance.png`](../../artifacts/rncp/screenshots/P08_ajout_exercice_dans_seance.png) |
| P09 | Gestion de plusieurs séries dans un exercice | Clic sur « Ajouter une série », puis renseignement de plusieurs lignes de série | BC01-C1, BC01-C2, BC03-C7 | [`P09_ajout_series_exercice.png`](../../artifacts/rncp/screenshots/P09_ajout_series_exercice.png) |
| P10 | Suppression contrôlée d’un exercice avant l’enregistrement de la séance | Clic sur l’action de retrait de l’exercice et affichage de la confirmation associée | BC01-C2, BC01-C5, BC01-C7, BC03-C7 | [`P10_suppression_exercice.png`](../../artifacts/rncp/screenshots/P10_suppression_exercice.png) |
| P11 | Retour explicite de succès après création d’une séance | Validation du formulaire complet et réception du message de succès | BC01-C1, BC01-C2, BC01-C5, BC03-C7 | [`P11_enregistrement_seance_succes.png`](../../artifacts/rncp/screenshots/P11_enregistrement_seance_succes.png) |
| P12 | Présence de la séance créée dans la liste avec les valeurs attendues | Retour automatique à la liste après l’enregistrement | BC01-C1, BC01-C5, BC03-C7 | [`P12_seance_visible_dans_liste.png`](../../artifacts/rncp/screenshots/P12_seance_visible_dans_liste.png) |
| P13 | Détail d’une séance : date, durée, difficulté, volume, exercices, séries et notes | Clic sur l’action de consultation d’une séance existante | BC01-C1, BC01-C2, BC01-C7, BC03-C7 | [`P13_detail_seance.png`](../../artifacts/rncp/screenshots/P13_detail_seance.png) |
| P14 | Formulaire de modification prérempli avec les données existantes | Clic sur « Modifier » depuis la séance créée | BC01-C1, BC01-C2, BC03-C7 | [`P14_modification_seance.png`](../../artifacts/rncp/screenshots/P14_modification_seance.png) |
| P15 | Protection contre une suppression involontaire de séance | Clic sur « Supprimer » et ouverture de la confirmation, sans valider l’action irréversible pour la capture | BC01-C2, BC01-C5, BC01-C7, BC03-C7 | [`P15_suppression_seance_confirmation.png`](../../artifacts/rncp/screenshots/P15_suppression_seance_confirmation.png) |

### 3.3 Objectifs

| ID | Fonction prouvée dans l’interface | Interaction réelle permettant d’atteindre l’état | Compétences RNCP principalement reliées | Image |
|---|---|---|---|---|
| P16 | Page Objectifs non vide avec cartes, progression et statuts distincts | Clic sur « Objectifs » et chargement des objectifs du compte | BC01-C1, BC01-C2, BC01-C7, BC03-C7 | [`P16_page_objectifs.png`](../../artifacts/rncp/screenshots/P16_page_objectifs.png) |
| P17 | Formulaire de création d’objectif sans données métier saisies, avec libellés, aides et valeurs par défaut attendues | Ouverture de la page Objectifs : seuls les paramètres usuels sont préinitialisés | BC01-C1, BC01-C2, BC01-C7, BC03-C7 | [`P17_creation_objectif_vide.png`](../../artifacts/rncp/screenshots/P17_creation_objectif_vide.png) |
| P18 | Formulaire d’objectif complété avec une cible réaliste | Saisie du nom, du type, de la compétence, de la cible, de l’unité, de l’échéance, de la priorité et des notes | BC01-C1, BC01-C2, BC03-C7 | [`P18_creation_objectif_rempli.png`](../../artifacts/rncp/screenshots/P18_creation_objectif_rempli.png) |
| P19 | Objectif actif avec valeur courante, cible, barre et pourcentage de progression | Enregistrement de l’objectif puis affichage de sa carte active | BC01-C1, BC01-C2, BC01-C7, BC03-C7 | [`P19_objectif_actif_progression.png`](../../artifacts/rncp/screenshots/P19_objectif_actif_progression.png) |
| P20 | Objectif terminé avec traitement visuel et statut explicite | Activation de l’action de finalisation sur un objectif actif | BC01-C1, BC01-C2, BC01-C5, BC03-C7 | [`P20_objectif_termine.png`](../../artifacts/rncp/screenshots/P20_objectif_termine.png) |
| P21 | Suppression contrôlée d’un objectif | Clic sur l’action de suppression et ouverture de la confirmation, sans valider l’action irréversible pour la capture | BC01-C2, BC01-C5, BC01-C7, BC03-C7 | [`P21_archivage_ou_suppression_objectif.png`](../../artifacts/rncp/screenshots/P21_archivage_ou_suppression_objectif.png) |

### 3.4 Import et export

| ID | Fonction prouvée dans l’interface | Interaction réelle permettant d’atteindre l’état | Compétences RNCP principalement reliées | Image |
|---|---|---|---|---|
| P22 | Page Import/Export structurée en zones CSV, JSON et protection des données | Clic sur « Import/Export » dans la navigation | BC01-C1, BC01-C2, BC01-C7, BC04-C4 | [`P22_page_import_export.png`](../../artifacts/rncp/screenshots/P22_page_import_export.png) |
| P23 | Documentation visible du format CSV, des colonnes et de l’exemple téléchargeable | Consultation de l’aide de format sur la page Import/Export | BC01-C1, BC01-C2, BC04-C4 | [`P23_format_csv_attendu.png`](../../artifacts/rncp/screenshots/P23_format_csv_attendu.png) |
| P24 | Sélection d’un fichier CSV avec consigne et action d’import explicites | Choix d’un fichier au moyen du sélecteur de l’interface | BC01-C1, BC01-C2, BC01-C7, BC03-C7, BC04-C4 | [`P24_import_csv_selection_fichier.png`](../../artifacts/rncp/screenshots/P24_import_csv_selection_fichier.png) |
| P25 | Rapport d’import valide avec nombres de lignes importées, ignorées et en erreur | Sélection d’un jeu CSV valide puis clic sur l’action d’import | BC01-C5, BC03-C7, BC04-C4 | [`P25_import_csv_succes.png`](../../artifacts/rncp/screenshots/P25_import_csv_succes.png) |
| P26 | Rapport d’erreur exploitable après import d’un fichier invalide | Sélection d’un jeu CSV invalide puis clic sur l’action d’import | BC01-C2, BC01-C5, BC03-C7, BC04-C4 | [`P26_import_csv_erreur.png`](../../artifacts/rncp/screenshots/P26_import_csv_erreur.png) |
| P27 | Déclenchement de l’export CSV et retour utilisateur visible | Clic sur « Export CSV », réception du téléchargement et affichage du feedback | BC01-C2, BC01-C5, BC03-C7, BC04-C4 | [`P27_export_csv.png`](../../artifacts/rncp/screenshots/P27_export_csv.png) |
| P28 | Déclenchement de l’export JSON et retour utilisateur visible | Clic sur « Export JSON », réception du téléchargement et affichage du feedback | BC01-C2, BC01-C5, BC03-C7, BC04-C4 | [`P28_export_json.png`](../../artifacts/rncp/screenshots/P28_export_json.png) |

### 3.5 Profil et protection des données

| ID | Fonction prouvée dans l’interface | Interaction réelle permettant d’atteindre l’état | Compétences RNCP principalement reliées | Image |
|---|---|---|---|---|
| P29 | Page Profil avec identité du compte, résumé et zone dédiée aux droits sur les données | Clic sur « Profil » dans la navigation authentifiée | BC01-C1, BC01-C2, BC01-C7, BC04-C3 | [`P29_page_profil.png`](../../artifacts/rncp/screenshots/P29_page_profil.png) |
| P30 | Export des données personnelles avec explication et retour utilisateur | Clic sur « Exporter mes données », réception du fichier et affichage du feedback | BC01-C2, BC01-C5, BC03-C7, BC04-C3, BC04-C4 | [`P30_export_donnees_personnelles.png`](../../artifacts/rncp/screenshots/P30_export_donnees_personnelles.png) |
| P31 | Confirmation explicite avant suppression des données du compte | Clic sur l’action de suppression puis ouverture de la confirmation ; annulation sans supprimer le compte | BC01-C2, BC01-C5, BC01-C7, BC03-C7, BC04-C3 | [`P31_confirmation_suppression_donnees.png`](../../artifacts/rncp/screenshots/P31_confirmation_suppression_donnees.png) |
| P32 | Information RGPD visible sur les données personnelles, leur export et leur suppression | Consultation de la zone d’information du profil | BC01-C1, BC01-C2, BC01-C7, BC04-C3 | [`P32_message_rgpd.png`](../../artifacts/rncp/screenshots/P32_message_rgpd.png) |

## 4. Lecture croisée avec les validations techniques

| Compétence | Apport du lot P01–P32 | Validation complémentaire qui reste nécessaire |
|---|---|---|
| BC01-C1 | Rend visibles les résultats attendus et les procédures utilisateur des cinq parcours principaux | Cahier des charges, backlog, guide utilisateur et procédures formalisées |
| BC01-C2 | Montre les libellés, aides, états, confirmations et retours qui matérialisent les impératifs de qualité côté utilisateur | DoD, stratégie de tests, CI et contrôles de qualité non visibles |
| BC01-C5 | Documente des états nominaux, des erreurs d’import et des protections contre les suppressions involontaires | Tests automatisés, registre de bugs et non-régressions exécutées |
| BC01-C7 | Montre la cohérence visuelle, la hiérarchie, les formulaires et les messages sur les vues principales | Audit axe, navigation clavier, reflow et session lecteur d’écran humaine recommandée |
| BC03-C7 | Constitue un jeu d’observations des cas vides, remplis, réussis, invalides et destructifs | Jeux de données reproductibles, assertions backend/frontend et scénarios Playwright |
| BC04-C3 | Rend visibles les agrégats du dashboard et les droits d’export/suppression des données personnelles | Calculs métier, tests PostgreSQL, isolation propriétaire et registre RGPD |
| BC04-C4 | Montre le format attendu, la sélection de fichier, les rapports d’import et les téléchargements CSV/JSON | Contrôle du contenu exact, round-trip, erreurs API et tests d’interopérabilité |

## 5. Limites RNCP maintenues

Le lot P01–P32 consolide les preuves d’interface au sein du bilan des **26 compétences déjà démontrées**, pour les sept compétences reliées ci-dessus. Il ne modifie ni les deux statuts partiels ni les huit statuts « Externe requis » de la matrice.

En particulier, **ces captures ne remplacent aucune des huit preuves externes** : processus réel d’entreprise, réingénierie mesurée, cartographie validée, décision collective, coordination d’équipe, recette signée par un tiers, adhésion d’un décideur et interaction collaborative authentifiée doivent toujours être apportés sous forme de pièces datées et vérifiables.
