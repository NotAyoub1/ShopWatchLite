from src.contrat import Diagnostic, Signal

def est_repete(sig: Signal, vus: set) -> bool:
    cle = (sig.date, sig.origine, sig.service, sig.categorie, sig.texte)
    if cle in vus:
        return True
    vus.add(cle)
    return False

def compter_incidents(sig: Signal, compteur: dict) -> int:
    if sig.categorie == "JOURNAL" and sig.gravite in ("MAJEUR", "BLOQUANT"):
        compteur[sig.service] = compteur.get(sig.service, 0) + 1
        return compteur[sig.service]
    return 0


def chercher_fiches(sig: Signal, base: dict) -> list:
    texte = sig.texte.lower()
    return [conseil for mot, conseil in base.items() if mot.lower() in texte]


def evaluer(sig: Signal, nb_incidents: int = 0) -> str:
    if nb_incidents >= 4:
        return "BLOQUANT"
    return sig.gravite

def diagnostiquer(sig: Signal, base: dict, nb_incidents: int = 0) -> Diagnostic:
    raise NotImplementedError