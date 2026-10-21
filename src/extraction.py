import re

from src.contrat import Signal

_SENSIBLES = r"(password|pwd|token|secret|card|iban)"
_MOTIF_SENSIBLE = re.compile(_SENSIBLES + r"(\s*[=:]\s*)[^\s&,;]+", re.IGNORECASE)
_GRAVITE_JOURNAL = {
    "FATAL": "BLOQUANT",
    "CRITICAL": "BLOQUANT",
    "ERROR": "MAJEUR",
    "WARN": "MODERE",
    "WARNING": "MODERE",
}

def masquer_donnees(texte: str) -> str:
    raise _MOTIF_SENSIBLE.sub(r"\1\2[MASQUE]", texte)

def lire_journal(ligne: str, numero: int, origine: str = "PAIEMENT",
                 env: str = "production") -> Signal:
    champs = ligne.split(None, 4)
    if len(champs) < 5:
        raise ValueError(f"Ligne de journal invalide : {ligne!r}")
    jour, heure, service, niveau, message = champs
    gravite = _GRAVITE_JOURNAL.get(niveau.upper(), "MINEUR")
    return Signal(
        ref=_ref(numero),
        date=f"{jour}T{heure}Z",
        origine=origine,
        service=service,
        env=env,
        categorie="JOURNAL",
        gravite=gravite,
        texte=masquer_donnees(message),
    )

def lire_scan(rapport: dict, numero: int, env: str = "production") -> Signal:
    raise NotImplementedError

def lire_build(rapport: dict, numero: int, env: str = "production") -> Signal:
    raise NotImplementedError

def _ref(numero: int) -> str:
    return f"SH-{numero:04d}"