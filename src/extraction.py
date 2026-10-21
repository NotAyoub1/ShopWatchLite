import re

from src.contrat import Signal

_SENSIBLES = r"(password|pwd|token|secret|card|iban)"
_MOTIF_SENSIBLE = re.compile(_SENSIBLES + r"(\s*[=:]\s*)[^\s&,;]+", re.IGNORECASE)
_MOTIF_BEARER = re.compile(r"(\bBearer\s+)[^\s&,;]+", re.IGNORECASE)
_GRAVITE_JOURNAL = {
    "FATAL": "BLOQUANT",
    "CRITICAL": "BLOQUANT",
    "ERROR": "MAJEUR",
    "WARN": "MODERE",
    "WARNING": "MODERE",
}
_GRAVITE_SCAN = {"critique": "BLOQUANT", "haut": "MAJEUR", "moyen": "MODERE"}

def masquer_donnees(texte: str) -> str:
    texte = _MOTIF_SENSIBLE.sub(r"\1\2[MASQUE]", texte)
    return _MOTIF_BEARER.sub(r"\1[MASQUE]", texte)

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

def _ref(numero: int) -> str:
    return f"SH-{numero:04d}"

def _verifier_cles(rapport: dict, cles: tuple) -> None:
    manquantes = [c for c in cles if c not in rapport]
    if manquantes:
        raise ValueError(f"Cle(s) manquante(s) : {', '.join(manquantes)}")


def lire_scan(rapport: dict, numero: int, env: str = "production") -> Signal:
    _verifier_cles(rapport, ("id_faille", "paquet", "risque", "date"))
    gravite = _GRAVITE_SCAN.get(str(rapport["risque"]).lower(), "MINEUR")
    return Signal(
        ref=_ref(numero),
        date=rapport["date"],
        origine="SCANNER",
        service=rapport["paquet"],
        env=env,
        categorie="FAILLE",
        gravite=gravite,
        texte=f"Faille {rapport['id_faille']} dans {rapport['paquet']}",
    )


def lire_build(rapport: dict, numero: int, env: str = "production") -> Signal:
    _verifier_cles(rapport, ("etape", "resultat", "date"))
    echec = str(rapport["resultat"]).lower() == "echec"
    return Signal(
        ref=_ref(numero),
        date=rapport["date"],
        origine="BUILD",
        service=rapport["etape"],
        env=env,
        categorie="BUILD_ECHEC" if echec else "BUILD_OK",
        gravite="MAJEUR" if echec else "MINEUR",
        texte=f"Build {rapport['etape']} : {rapport['resultat']}",
    )