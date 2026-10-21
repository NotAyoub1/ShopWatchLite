import unittest

from src.extraction import masquer_donnees


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


if __name__ == "__main__":
    unittest.main()