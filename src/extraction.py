import re

from src.contrat import Signal

_SENSIBLES = r"(password|pwd|token|secret|card|iban)"
_MOTIF_SENSIBLE = re.compile(_SENSIBLES + r"(\s*[=:]\s*)[^\s&,;]+", re.IGNORECASE)

def masquer_donnees(texte: str) -> str:
    raise _MOTIF_SENSIBLE.sub(r"\1\2[MASQUE]", texte)

def lire_journal(ligne: str, numero: int, origine: str = "PAIEMENT",
        env: str = "production") -> Signal:
    raise NotImplementedError

def lire_scan(rapport: dict, numero: int, env: str = "production") -> Signal:
    raise NotImplementedError

def lire_build(rapport: dict, numero: int, env: str = "production") -> Signal:
    raise NotImplementedError