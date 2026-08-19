# D1-01 — Architecture SkillTrack

## Contexte

```mermaid
C4Context
  Person(user, "Pratiquant", "Suit ses séances et exporte ses données")
  System(skilltrack, "SkillTrack", "Application web de suivi calisthénie")
  System_Ext(mailhog, "MailHog", "Service SMTP de test")
  Rel(user, skilltrack, "Utilise", "HTTPS/JSON")
  Rel(skilltrack, mailhog, "Envoie emails de test", "SMTP")
```

## Conteneurs

```mermaid
flowchart LR
  U[Utilisateur] --> F[Frontend React]
  F --> A[API FastAPI]
  A --> S[Services métier]
  S --> R[Repositories]
  R --> DB[(PostgreSQL)]
  A --> M[MailHog SMTP]
```

## Responsabilités

| Composant | Responsabilité | Tests |
|---|---|---|
| Frontend | Formulaires, dashboard, accessibilité | Vitest, audit RGAA |
| API | Contrats HTTP, auth, validation | TestClient |
| Services | Règles métier | pytest |
| Repositories | Accès données | tests substitution/mémoire |
| PostgreSQL | Contraintes, index, transactions | tests intégrité |
