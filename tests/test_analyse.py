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
# compter_incidents
    def test_compter_incidents(self):
        compteur = {}
        self.assertEqual(compter_incidents(sig(), compteur), 1)
        self.assertEqual(compter_incidents(sig(gravite="BLOQUANT"), compteur), 2)
        self.assertEqual(compteur, {"paiement": 2})

    def test_compter_ignore_mineur_et_non_journal(self):
        compteur = {}
        self.assertEqual(compter_incidents(sig(gravite="MINEUR"), compteur), 0)
        self.assertEqual(compter_incidents(sig(categorie="FAILLE"), compteur), 0)
        self.assertEqual(compteur, {})

    # chercher_fiches
    def test_chercher_fiches(self):
        res = chercher_fiches(sig(texte="TIMEOUT sur la passerelle"), FICHES)
        self.assertEqual(res, [FICHES["timeout"]])

    def test_chercher_fiches_vide(self):
        self.assertEqual(chercher_fiches(sig(texte="Service demarre"), FICHES), [])

    # evaluer
    def test_evaluer_panne_en_boucle(self):
        s = sig()
        self.assertEqual(evaluer(s, 4), "BLOQUANT")
        self.assertEqual(evaluer(s, 3), "MAJEUR")

    def test_evaluer_gravite_du_signal(self):
        self.assertEqual(evaluer(sig(gravite="MODERE")), "MODERE")
   
if __name__ == "__main__":
    unittest.main()