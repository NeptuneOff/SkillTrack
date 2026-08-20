# H-RGAA — Audit d'accessibilité ciblé

## 1. Référentiel et portée

Cible documentaire : [RGAA 4.1.2 officiel](https://accessibilite.numerique.gouv.fr/), fondé sur WCAG 2.1 A/AA. Cette version reste celle publiée par la DINUM au 19/08/2026 ; le RGAA 5 est annoncé mais pas encore publié. Pages prioritaires : connexion, dashboard, séances/formulaire, objectifs, import/export et profil. Ce document est un audit de préparation, pas une déclaration officielle de conformité.

Statuts : **OK statique** = présence vérifiable dans le code ; **OK navigateur** = contrôle exécuté dans Chromium sur l'interface réelle ; **à tester** = contrôle humain non archivé ; **écart** = correction connue.

## 2. Résultats de revue statique

| Contrôle | Résultat | Preuve/écart |
|---|---|---|
| Titre de page et langue | OK statique | `<html lang="fr">`, titre et description dans `frontend/index.html` |
| Hiérarchie des titres | OK navigateur ciblé | `<h1>` par page et aucune violation/incomplétude axe sur les cinq vues connectées |
| Labels formulaires | OK statique sur principaux formulaires | labels login/séance/import ; formulaire `frontend/src/GoalsPage.jsx` |
| Aides/placeholders/bornes | OK statique sur séances/objectifs | HTML `required/min/max` + Pydantic côté API |
| Erreurs identifiables | OK structurel ciblé | alertes/status nommés et aucun attribut ARIA invalide après correction navigateur |
| Retour d'opération | OK statique | toast, `role="status"` sur rapport d'import |
| Nom accessible des boutons icônes | OK structurel ciblé | texte visible ou `aria-label`; axe ne relève pas de bouton sans nom sur les six vues |
| Progression objectif | Partiel | `aria-label` présent, information aussi textuelle |
| Focus visible | OK navigateur ciblé | lien d'évitement, champs et bouton de connexion atteints ; règle `:focus-visible` explicite |
| Navigation clavier | OK navigateur ciblé | lien d'évitement, Tab, Entrée, connexion et cinq entrées de navigation contrôlés |
| Audit axe automatisé | OK navigateur | règles par défaut, contrastes inclus : 0 violation et 0 résultat incomplet sur cinq vues connectées |
| Contrastes | OK axe navigateur | surfaces rendues déterministes après correction des dégradés ; 0 violation/incomplétude |
| Zoom 400 % / reflow | OK navigateur | aucune largeur document supérieure au viewport à 320 CSS px sur cinq vues |
| Lecteur d'écran | À tester | NVDA/VoiceOver non exécuté dans le dépôt |
| Réduction des animations | OK statique | règle `prefers-reduced-motion: reduce` dans `improvements.css` |

## 3. Protocole reproductible

Pour chaque page, conserver date, navigateur, résolution et version du commit.

1. Déconnecter la souris ; parcourir avec Tab/Shift+Tab, activer avec Entrée/Espace, fermer avec Échap.
2. Vérifier que le focus reste visible, logique et ne se perd pas après chargement/erreur.
3. À 200 % puis 400 %, vérifier absence de perte d'information et de défilement horizontal bloquant.
4. Exécuter axe DevTools ou Lighthouse et exporter le rapport HTML/JSON.
5. Contrôler les contrastes texte/fond et focus avec un outil dédié.
6. Avec NVDA + Firefox ou VoiceOver + Safari, lire connexion, création séance, rapport import et confirmation de suppression.
7. Provoquer une erreur par formulaire ; vérifier annonce, libellé et correction possible.

## 4. Résultat navigateur archivé

Audit du 19/08/2026 : `frontend/e2e/accessibility.spec.js` contre l'interface, l'API et PostgreSQL réels. Preuves durables : `artifacts/accessibility/2026-08-19-browser-audit.md` et synthèse du run 2/2 `artifacts/accessibility/2026-08-19-playwright.md`.

| Vue | Règles axe validées | À revoir | Violations | Reflow 320 px |
|---|---:|---:|---:|---|
| Dashboard | 35 | 0 | 0 | OK |
| Séances | 39 | 0 | 0 | OK |
| Objectifs | 39 | 0 | 0 | OK |
| Import / Export | 41 | 0 | 0 | OK |
| Profil RGPD | 35 | 0 | 0 | OK |

Les premiers passages ont détecté le débordement de l'exemple CSV puis de la table chargée avec sept historiques réels, des attributs ARIA inapplicables et des contrastes rendus indéterminables par des dégradés. Ces écarts ont été corrigés ; le test attend les loaders et échoue désormais également si axe classe un contrôle « incomplete ». Le rapport Playwright joint le JSON axe et une capture du reflow.

## 5. Critères de sortie

- aucun blocage clavier sur le parcours jury ;
- aucune erreur axe critique/sérieuse non justifiée ;
- contraste texte normal ≥ 4,5:1, grand texte ≥ 3:1 et composants/focus ≥ 3:1 ;
- erreurs perceptibles autrement que par la couleur ;
- contenu utilisable à 200 % et réorganisé à 320 CSS px ;
- session lecteur d'écran humaine et PV par une personne distincte recommandés avant exposition publique.

Le périmètre technique MVP est démontré par une exécution datée sur clavier, moteur axe réel et reflow 320 px. Cela ne constitue ni un audit exhaustif des 106 critères, ni une déclaration officielle de conformité RGAA. Une session humaine avec NVDA, JAWS ou VoiceOver reste à réaliser avant une mise en production publique.

Preuves complémentaires : `frontend/src/app.test.jsx` contrôle structurellement la connexion et les cinq vues dans jsdom ; `frontend/e2e/accessibility.spec.js` injecte axe-core dans Chromium, contrastes inclus, puis vérifie clavier et reflow. La connexion est couverte par le test structurel et le parcours clavier ; les résultats axe navigateur chiffrés portent sur les cinq vues après authentification.
