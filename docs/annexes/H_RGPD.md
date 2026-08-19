# H-RGPD — Registre de traitement et contrôles

Références de contrôle : [texte du RGPD et droits des personnes — CNIL](https://www.cnil.fr/fr/reglement-europeen-protection-donnees), [premières étapes de conformité — CNIL](https://www.cnil.fr/fr/passer-laction/rgpd-les-premieres-etapes) et [durées de conservation — CNIL](https://www.cnil.fr/fr/passer-laction/les-durees-de-conservation-des-donnees). Cette annexe décrit le MVP et ne remplace pas l'analyse juridique du contexte réel de mise à disposition.

## 1. Fiche de traitement

| Élément | Description |
|---|---|
| Traitement | suivi personnel d'entraînements de calisthénie |
| Responsable | porteur du projet pédagogique — identité/coordonnées à compléter dans le dossier privé |
| Personnes concernées | utilisateurs de SkillTrack |
| Finalité | journaliser les séances, calculer la progression, définir des objectifs, importer/exporter |
| Base juridique cible | exécution du service demandé ; à confirmer selon le contexte réel de mise à disposition |
| Données | e-mail, nom affiché, séances, exercices, objectifs, notes, historique d'import |
| Données exclues | diagnostic, pathologie, biométrie et coaching médical |
| Destinataires | utilisateur propriétaire ; administrateur technique uniquement si nécessaire |
| Transfert hors UE | aucun flux tiers identifié dans le MVP local |
| Conservation cible | pendant la vie du compte puis suppression ; sauvegardes/logs à définir avant production |
| Sous-traitants | aucun en local ; hébergeur à documenter si déploiement |

## 2. Minimisation et privacy by design

- aucun nom légal, adresse, téléphone, paiement ou donnée de santé n'est requis ;
- l'e-mail sert à l'authentification ; le nom affiché sert à l'interface ;
- les notes sont libres : l'aide utilisateur doit déconseiller les données sensibles ;
- chaque requête métier exploite le propriétaire issu du JWT ;
- les données de démonstration sont fictives.

## 3. Droits et implémentation

| Droit/principe | Parcours | Preuve | Contrôle restant |
|---|---|---|---|
| Accès | page Profil + API `/users/me` | `backend/app/main.py:me`, `frontend/src/ProfilePage.jsx` | guide de contact hors application |
| Portabilité | exports JSON/CSV | `/exports/json`, `/exports/csv` | recette exhaustive du contenu |
| Effacement | confirmation puis `DELETE /users/me` | `backend/app/main.py:delete_me`, cascades modèles, test de portée | vérifier la politique des sauvegardes |
| Rectification | CRUD séances/objectifs | routes PUT et formulaires | modification e-mail/nom non livrée |
| Limitation/opposition | pas de parcours livré | — | déterminer l'applicabilité selon la base légale réelle et définir le processus |
| Transparence | texte Profil + présent registre | `frontend/src/ProfilePage.jsx` | politique de confidentialité accessible |

## 4. Flux et cloisonnement

```text
Utilisateur → navigateur (JWT localStorage)
→ API → PostgreSQL
← exports téléchargés sur le poste de l'utilisateur
```

Aucun tracker analytique ou appel publicitaire n'est identifié. Le stockage du JWT dans `localStorage` est un risque XSS documenté dans `F_securite.md`.

## 5. Agrégats et export

Les statistiques (`backend/app/services.py:dashboard`) sont calculées à partir des séances du propriétaire obtenues par le repository. Les exports (`data_exchange.py:build_json_export` et `build_csv_export`) appliquent le même port filtré et incluent profil, séances/exercices, objectifs et historique d'import. Les tests comparent deux propriétaires, le contenu des agrégats/exports et la portée d'effacement.

## 6. Procédure d'exercice d'un droit

1. authentifier le demandeur ;
2. consigner la date, le droit et le périmètre sans copier les données dans le ticket ;
3. exporter ou corriger depuis le parcours prévu ;
4. pour l'effacement, ne pas créer de nouvelle copie ; supprimer/cascader et appliquer aux sauvegardes une durée/purge documentée compatible avec les obligations réelles ;
5. vérifier l'absence des données actives par requêtes de contrôle ;
6. répondre au demandeur dans le délai applicable et archiver une preuve minimale de traitement.

## 7. Points obligatoires avant production

- fixer durées de conservation des comptes, logs et sauvegardes ;
- renseigner responsable, contact, hébergeur et transferts ;
- publier une information de confidentialité ;
- définir procédure de violation et registre des demandes ;
- réaliser une analyse d'impact si le périmètre évolue vers des données de santé ou un suivi systématique.
