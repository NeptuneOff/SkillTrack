# H-RGAA-01 — Audit accessibilité ciblé

Version ciblée : RGAA 4.1.2 / WCAG AA.

## Parcours audités

1. Connexion.
2. Création d'une séance.
3. Consultation du dashboard.
4. Import CSV et lecture du rapport.

## Critères à vérifier

| Critère | Méthode | Preuve |
|---|---|---|
| Navigation clavier | Tab complet sans piège | capture/video |
| Focus visible | contrôle manuel CSS | capture avant/après |
| Labels de champs | inspection DOM | rapport |
| Contrastes | Lighthouse + contrôle manuel | rapport |
| Messages d'erreur | lecteur d'écran ciblé | note test |
| Titres structurés | inspection HTML | capture |
