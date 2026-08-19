# H-RGPD-01 — Registre RGPD

## Traitement

Suivi d'entraînement personnel dans SkillTrack.

| Élément | Description |
|---|---|
| Responsable | Karl Daval-Leclercq, projet pédagogique |
| Finalité | Permettre à l'utilisateur de journaliser ses séances et suivre ses progressions |
| Base légale | Consentement / exécution du service demandé dans le cadre du MVP pédagogique |
| Données | email, nom affiché, séances, exercices, séries, notes d'entraînement |
| Données sensibles | Non collectées dans le MVP ; pas de pathologie, santé, biométrie ou diagnostic |
| Destinataires | Utilisateur propriétaire ; aucun tiers commercial |
| Durée | Compte actif + suppression à la demande ; logs techniques 90 jours maximum en cible |
| Droits | accès, rectification, export, suppression |
| Sécurité | hash, JWT, filtrage user_id, sauvegarde, tests d'accès croisé |

## Agrégats

Les statistiques sont calculées à partir des données appartenant à l'utilisateur connecté. Les tests doivent vérifier qu'aucun agrégat ne mélange deux propriétaires.
