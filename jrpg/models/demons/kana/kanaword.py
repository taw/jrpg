# -*- coding: UTF-8 -*-

from demonsoul import DemonSoul

from romajitokana import romaji_kana_match

class DemonSoulKanaword(DemonSoul):
    def __init__(self, kanaword, romajis, meanings):
        self.kanaword = kanaword
        self.romajis = romajis
        self.meanings = [meanings]
        # Some wishful thinking:
        #kunrei = canonical_kunrei(displayed_name)
        #hepburn = canonical_hepburn(displayed_name)
        #if kunrei == hepburn:
        #    self.romajis = [kunrei]
        #else:
        #    self.romajis = [kunrei, hepburn]

    def xp_code(self):
        return self.kanaword + ":" + (":".join(self.romajis))

    def xp_for_win(self):
        return 2

    def short_dn(self):
        return self.kanaword

    def furicode(self):
        return [(self.kanaword, None, False)]

    def secret_names(self):
        return self.romajis

    def meanings(self):
        return self.meanings

    def answer_ok(self, secret_name_guess):
        if romaji_kana_match(secret_name_guess, self.kanaword):
            return True
        return False

    def get_good_response(self):
        return self.romajis

    def hardcore_mode(self):
        return True

