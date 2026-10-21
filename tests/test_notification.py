import unittest

from src.contrat import Diagnostic, Signal
from src.notification import (approuver, choisir_canal, composer,
                              consigner, diffuser)


def exemple(critique=True, niveau="BLOQUANT"):
    s = Signal("SH-0125", "2026-11-27T17:02:11Z", "PAIEMENT", "paiement",
               "production", "JOURNAL", "MAJEUR", "timeout passerelle apres 30s")
    d = Diagnostic("SH-0125", niveau, "Passerelle lente",
                   "Isoler le service paiement", critique, ["PAIEMENT"])
    return s, d


class TestNotification(unittest.TestCase):
    def test_canaux(self):
        self.assertEqual(choisir_canal("BLOQUANT"), "SLACK")
        self.assertEqual(choisir_canal("MAJEUR"), "TEAMS")
        self.assertEqual(choisir_canal("MODERE"), "EMAIL")
        self.assertEqual(choisir_canal("MINEUR"), "TABLEAU")

    def test_canal_invalide(self):
        with self.assertRaises(ValueError):
            choisir_canal("INCONNU")

    def test_composer(self):
        s, d = exemple()
        self.assertEqual(composer(s, d), "\n".join([
            "*** BLOQUANT *** Service : paiement",
            "Constat : timeout passerelle apres 30s",
            "Cause : Passerelle lente",
            "A faire : Isoler le service paiement",
            "Origines : PAIEMENT",
        ]))

    def test_composer_origines_multiples(self):
        s, d = exemple()
        d.origines = ["PAIEMENT", "SCANNER"]
        self.assertTrue(composer(s, d).endswith("Origines : PAIEMENT + SCANNER"))

    def test_diffuser(self):
        s, d = exemple()
        registre = []
        msg = diffuser(s, d, registre)
        self.assertEqual(msg.canal, "SLACK")
        self.assertEqual(msg.destinataire, "astreinte-shop")
        self.assertEqual(msg.signal_ref, "SH-0125")
        self.assertEqual(msg.contenu, composer(s, d))
        self.assertEqual(registre, [msg])
        self.assertEqual(s.etat, "DIFFUSE")

    def test_approbation(self):
        _, d = exemple()
        self.assertTrue(approuver(d, " OUI "))
        self.assertTrue(approuver(d, "o"))
        self.assertTrue(approuver(d, "Ok"))
        self.assertTrue(approuver(d, "yes"))
        self.assertFalse(approuver(d, "n"))
        self.assertFalse(approuver(d, ""))

    def test_approbation_non_critique(self):
        _, d = exemple(critique=False, niveau="MINEUR")
        self.assertTrue(approuver(d, "n"))

    def test_consigner(self):
        _, d = exemple()
        carnet = []
        e = consigner(d, True, "astreinte-shop", carnet, "2026-11-27T17:10:00Z")
        self.assertEqual(e, {
            "ref": "SH-0125",
            "action": "Isoler le service paiement",
            "accord": True,
            "responsable": "astreinte-shop",
            "instant": "2026-11-27T17:10:00Z",
        })
        self.assertEqual(carnet, [e])


if __name__ == "__main__":
    unittest.main()