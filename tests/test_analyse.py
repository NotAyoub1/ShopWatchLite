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



    # diagnostiquer
    def test_diag_inconnu_observer(self):
        d = diagnostiquer(sig(gravite="MINEUR", texte="Service demarre"), FICHES)
        self.assertEqual(d.cause, "Cause inconnue : verification manuelle")
        self.assertEqual(d.action, "Observer")
        self.assertFalse(d.critique)
        self.assertEqual(d.origines, ["PAIEMENT"])

    def test_diag_isoler_si_bloquant(self):
        s = sig()
        d = diagnostiquer(s, FICHES, 4)
        self.assertEqual(d.niveau, "BLOQUANT")
        self.assertEqual(d.action, "Isoler le service paiement")
        self.assertTrue(d.critique)
        self.assertEqual(s.etat, "EVALUE")

    def test_diag_faille(self):
        s = sig(categorie="FAILLE", gravite="BLOQUANT", service="lib-panier",
                texte="Faille CVE-2026-7788 dans lib-panier")
        d = diagnostiquer(s, FICHES)
        self.assertEqual(d.action, "Corriger la dependance lib-panier")
        self.assertFalse(d.critique)

    def test_diag_build_echec(self):
        s = sig(categorie="BUILD_ECHEC", service="deploiement",
                texte="Build deploiement : echec")
        d = diagnostiquer(s, FICHES)
        self.assertEqual(d.action, "Rejouer le build deploiement")
        self.assertIn(FICHES["build"], d.cause)

    def test_diag_causes_multiples(self):
        s = sig(texte="build timeout")
        d = diagnostiquer(s, FICHES)
        self.assertEqual(d.cause, FICHES["timeout"] + " ; " + FICHES["build"])
   
if __name__ == "__main__":
    unittest.main()