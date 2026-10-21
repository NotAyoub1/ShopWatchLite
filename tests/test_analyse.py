import unittest

from src.analyse import (chercher_fiches, compter_incidents, diagnostiquer,
                         est_repete, evaluer)
from src.contrat import FICHES, Signal


def sig(categorie="JOURNAL", gravite="MAJEUR", texte="timeout passerelle apres 30s",
        service="paiement"):
    return Signal("SH-0001", "2026-11-27T17:00:00Z", "PAIEMENT", service,
                  "production", categorie, gravite, texte)


class TestAnalyse(unittest.TestCase):
    # est_repete
    def test_repete(self):
        vus = set()
        self.assertFalse(est_repete(sig(), vus))
        self.assertTrue(est_repete(sig(), vus))

    def test_non_repete_si_date_differente(self):
        vus = set()
        a = sig()
        b = sig()
        b.date = "2026-11-27T17:00:01Z"
        self.assertFalse(est_repete(a, vus))
        self.assertFalse(est_repete(b, vus))

   
if __name__ == "__main__":
    unittest.main()