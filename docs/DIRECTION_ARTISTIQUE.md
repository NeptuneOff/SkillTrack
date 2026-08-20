# Direction artistique et principes UX — Nocturne Kinetic

## Intention

L'identité associe précision sportive et lecture analytique : fond bleu-noir, surfaces légèrement translucides, accents menthe/cyan et indicateurs compacts. Elle doit aider à lire l'information, jamais remplacer une hiérarchie ou un libellé.

## Parcours et priorités

1. **Connexion** : compte démo visible, deux champs explicitement étiquetés, erreur actionnable.
2. **Dashboard** : métriques en premier, puis tendance, séances et objectifs récents.
3. **Séances** : liste/détail, action principale visible, formulaire progressif et suppression confirmée.
4. **Objectifs** : cible et progression mesurables, cycle complet explicite.
5. **Import/Export** : format avant sélection, résultat accepté/rejeté après traitement.
6. **Profil** : droits RGPD en langage simple, action destructive isolée.

## Système visuel

| Élément | Règle |
|---|---|
| Couleurs | bleu-noir pour fond ; cyan/menthe pour action/progression ; rouge réservé au danger |
| Typographie | taille lisible, hiérarchie h1/h2/h3, texte secondaire jamais seule source d'information |
| Cartes | regroupent une tâche ou un ensemble cohérent, sans imbrication décorative inutile |
| Boutons | verbe d'action visible ; primaire unique par contexte ; état désactivé perceptible |
| Formulaires | label persistant, aide avant action, exemple en placeholder, erreur près du contexte |
| Feedback | chargement, état vide, succès et erreur présents ; aucune page ne devient vide sur exception |
| Responsive | grille réorganisée sur petit écran ; actions accessibles sans survol |

## Accessibilité et sobriété

- l'information n'est pas portée uniquement par la couleur ou une icône ;
- les icônes accompagnent un texte sur les actions importantes ;
- les erreurs utilisent des rôles/annonces adaptées ;
- les transitions restent courtes et doivent respecter `prefers-reduced-motion` ;
- aucune vidéo, photo lourde ou polling n'est nécessaire au parcours principal.

La palette et les principes ne suffisent pas à déclarer une conformité. L'audit navigateur clavier/contraste/reflow est archivé et la session lecteur d'écran humaine restante est définie dans `annexes/H_RGAA.md`.

## États à vérifier avant jury

Pour chaque page : chargement, données, liste vide, erreur API, succès, action destructive, écran étroit et retour après navigation. Capturer au moins le dashboard, un formulaire rempli, un rapport d'import et une erreur accessible sur le commit présenté.
