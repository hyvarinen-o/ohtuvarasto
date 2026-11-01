import unittest
from varasto import Varasto


class TestVarasto(unittest.TestCase):
    def setUp(self):
        self.varasto = Varasto(10)

    def test_konstruktori_luo_tyhjan_varaston(self):
        # https://docs.python.org/3/library/unittest.html#unittest.TestCase.assertAlmostEqual
        self.assertAlmostEqual(self.varasto.saldo, 0)

    def test_uudella_varastolla_oikea_tilavuus(self):
        self.assertAlmostEqual(self.varasto.tilavuus, 10)

    def test_lisays_lisaa_saldoa(self):
        self.varasto.lisaa_varastoon(8)

        self.assertAlmostEqual(self.varasto.saldo, 8)

    def test_lisays_lisaa_pienentaa_vapaata_tilaa(self):
        self.varasto.lisaa_varastoon(8)

        # vapaata tilaa pitäisi vielä olla tilavuus-lisättävä määrä eli 2
        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 2)

    def test_ottaminen_palauttaa_oikean_maaran(self):
        self.varasto.lisaa_varastoon(8)

        saatu_maara = self.varasto.ota_varastosta(2)

        self.assertAlmostEqual(saatu_maara, 2)

    def test_ottaminen_lisaa_tilaa(self):
        self.varasto.lisaa_varastoon(8)

        self.varasto.ota_varastosta(2)

        # varastossa pitäisi olla tilaa 10 - 8 + 2 eli 4
        self.assertAlmostEqual(self.varasto.paljonko_mahtuu(), 4)

    def test_liikaa_ottaminen_ottaa_maksimin(self):
        self.varasto.lisaa_varastoon(2)
        saatu = self.varasto.ota_varastosta(4)
        self.assertAlmostEqual(saatu, 2)

    def test_liikaa_tavaraa_lisays(self):
        self.varasto.lisaa_varastoon(8)
        self.varasto.lisaa_varastoon(4)
        saldo = self.varasto.saldo
        self.assertAlmostEqual(saldo, 10)

    def test_virheellinen_tilavuus_asetetaan_nollaan(self):
        varasto = Varasto(-1)
        self.assertAlmostEqual(varasto.tilavuus, 0)

    def test_virheellinen_alkusaldo_asetetaan_nollaan(self):
        varasto = Varasto(10, -1)
        self.assertAlmostEqual(varasto.saldo, 0)

    def test_virheellinen_lisays_ei_muutoksia(self):
        self.varasto.lisaa_varastoon(-1)
        self.assertAlmostEqual(self.varasto.tilavuus, 10)

    def test_virheellinen_lisays_palauttaa_nolla(self):
        saatu = self.varasto.ota_varastosta(-1)
        self.assertAlmostEqual(saatu, 0)

    def test_str_esitys_oikea(self):
        oikea = f"saldo = {self.varasto.saldo}, vielä tilaa {self.varasto.paljonko_mahtuu()}"
        self.assertAlmostEqual(oikea, str(self.varasto))