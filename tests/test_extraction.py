import unittest

from src.extraction import masquer_donnees, lire_journal, lire_build, lire_scan

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


    def test_lire_scan(self):
        rapport = {"id_faille": "CVE-2026-7788", "paquet": "lib-panier",
                   "risque": "critique", "date": "2026-11-27T17:09:00Z"}
        sig = lire_scan(rapport, 9)
        self.assertEqual(sig.ref, "SH-0009")
        self.assertEqual(sig.origine, "SCANNER")
        self.assertEqual(sig.service, "lib-panier")
        self.assertEqual(sig.categorie, "FAILLE")
        self.assertEqual(sig.date, "2026-11-27T17:09:00Z")
        self.assertEqual(sig.gravite, "BLOQUANT")
        self.assertEqual(sig.texte, "Faille CVE-2026-7788 dans lib-panier")

    def test_gravites_scan(self):
        attendu = {"critique": "BLOQUANT", "HAUT": "MAJEUR",
                   "Moyen": "MODERE", "faible": "MINEUR"}
        for risque, gravite in attendu.items():
            rapport = {"id_faille": "CVE-1", "paquet": "p", "risque": risque,
                       "date": "2026-11-27T17:00:00Z"}
            self.assertEqual(lire_scan(rapport, 1).gravite, gravite, risque)

    def test_lire_scan_cle_manquante(self):
        with self.assertRaises(ValueError):
            lire_scan({"id_faille": "CVE-1", "paquet": "p", "risque": "haut"}, 1)

    def test_lire_build_echec(self):
        rapport = {"etape": "deploiement", "resultat": "ECHEC",
                   "date": "2026-11-27T17:08:00Z"}
        sig = lire_build(rapport, 8)
        self.assertEqual(sig.origine, "BUILD")
        self.assertEqual(sig.service, "deploiement")
        self.assertEqual(sig.categorie, "BUILD_ECHEC")
        self.assertEqual(sig.gravite, "MAJEUR")
        self.assertEqual(sig.texte, "Build deploiement : ECHEC")

    def test_lire_build_ok(self):
        rapport = {"etape": "tests", "resultat": "succes",
                   "date": "2026-11-27T17:08:00Z"}
        sig = lire_build(rapport, 3)
        self.assertEqual(sig.categorie, "BUILD_OK")
        self.assertEqual(sig.gravite, "MINEUR")

    def test_lire_build_cle_manquante(self):
        with self.assertRaises(ValueError):
            lire_build({"etape": "tests", "resultat": "echec"}, 1)


if __name__ == "__main__":
    unittest.main()