# -*- coding: UTF-8 -*-

import unittest
from romajitokana import romaji_kana_match

class RomajiToKanaTest(unittest.TestCase):
    def testKana(self):
        self.assertTrue(romaji_kana_match(U"a",U"あ"))
        self.assertTrue(romaji_kana_match(U"aa",U"あー"))
        self.assertTrue(romaji_kana_match(U"uu",U"うー"))
        self.assertTrue(romaji_kana_match(U"attaakkuu",U"あったーっくう"))
        self.assertTrue(romaji_kana_match(U"aaoo",U"あーおー"))
        self.assertTrue(romaji_kana_match(U"aaaa",U"あーーー"))
        self.assertFalse(romaji_kana_match(U"i",U"あ"))
        self.assertFalse(romaji_kana_match(U"aa",U"あ"))
        self.assertFalse(romaji_kana_match(U"ua",U"うー"))
        self.assertFalse(romaji_kana_match(U"au",U"うー"))
        self.assertFalse(romaji_kana_match(U"a",U"あー"))
        self.assertFalse(romaji_kana_match(U"aaaa",U"あーーい"))
