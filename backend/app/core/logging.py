from __future__ import annotations

import hashlib
import json
import logging
from typing import Any


def pseudonymous_reference(value: str) -> str:
    """Produit une référence corrélable sans journaliser l'identifiant utilisateur."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def log_event(logger: logging.Logger, level: int, event: str, **fields: Any) -> None:
    payload = {"event": event, **fields}
    logger.log(level, json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str))
