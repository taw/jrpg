import unittest
from romajitokana import romaji_kana_match


class RomajiToKanaTest(unittest.TestCase):
    def testKana(self):
        self.assertTrue(romaji_kana_match("a", "あ"))
        self.assertTrue(romaji_kana_match("aa", "あー"))
        self.assertTrue(romaji_kana_match("uu", "うー"))
        self.assertTrue(romaji_kana_match("attaakkuu", "あったーっくう"))
        self.assertTrue(romaji_kana_match("aaoo", "あーおー"))
        self.assertTrue(romaji_kana_match("aaaa", "あーーー"))
        self.assertFalse(romaji_kana_match("i", "あ"))
        self.assertFalse(romaji_kana_match("aa", "あ"))
        self.assertFalse(romaji_kana_match("ua", "うー"))
        self.assertFalse(romaji_kana_match("au", "うー"))
        self.assertFalse(romaji_kana_match("a", "あー"))
        self.assertFalse(romaji_kana_match("aaaa", "あーーい"))
