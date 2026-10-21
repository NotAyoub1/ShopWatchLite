import unittest

from src.extraction import masquer_donnees, lire_journal

LIGNE = ("2026-11-27 17:02:11 paiement ERROR timeout passerelle apres 30s "
         "card=4970123412341234")

class TestExtraction(unittest.TestCase):
    def test_masquer_donnees(self):
        self.assertEqual(masquer_donnees("client=bob pwd=abc123"),
                         "client=bob pwd=[MASQUE]")

    def test_masquer_casse_ignoree(self):
        self.assertEqual(masquer_donnees("PASSWORD=Abc Token=xyz"),
                         "PASSWORD=[MASQUE] Token=[MASQUE]")

    def test_masquer_forme_deux_points(self):
        self.assertEqual(masquer_donnees("secret: topsecret fin"),
                         "secret: [MASQUE] fin")

    def test_masquer_separateurs_de_valeur(self):
        self.assertEqual(masquer_donnees("a=1&card=4970&b=2"),
                         "a=1&card=[MASQUE]&b=2")
        self.assertEqual(masquer_donnees("iban=FR76,x=1;token=zz"),
                         "iban=[MASQUE],x=1;token=[MASQUE]")

    def test_masquer_rien_a_masquer(self):
        self.assertEqual(masquer_donnees("service demarre"), "service demarre")

    def test_lire_journal(self):
        sig = lire_journal(LIGNE, 42)
        self.assertEqual(sig.ref, "SH-0042")
        self.assertEqual(sig.date, "2026-11-27T17:02:11Z")
        self.assertEqual(sig.service, "paiement")
        self.assertEqual(sig.categorie, "JOURNAL")
        self.assertEqual(sig.origine, "PAIEMENT")
        self.assertEqual(sig.env, "production")
        self.assertEqual(sig.gravite, "MAJEUR")
        self.assertNotIn("4970123412341234", sig.texte)
        self.assertIn("card=[MASQUE]", sig.texte)

    def test_gravites_journal(self):
        attendu = {"FATAL": "BLOQUANT", "CRITICAL": "BLOQUANT",
                   "ERROR": "MAJEUR", "WARN": "MODERE",
                   "WARNING": "MODERE", "INFO": "MINEUR", "debug": "MINEUR",
                   "error": "MAJEUR"}
        for niveau, gravite in attendu.items():
            ligne = f"2026-11-27 17:00:00 paiement {niveau} message de test"
            self.assertEqual(lire_journal(ligne, 1).gravite, gravite, niveau)

    def test_lire_journal_ligne_trop_courte(self):
        with self.assertRaises(ValueError):
            lire_journal("2026-11-27 17:00:00 paiement ERROR", 1)


if __name__ == "__main__":
    unittest.main()