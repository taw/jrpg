# -*- coding: UTF-8 -*-

from demonsoul import DemonSoul
from romajitokana import romaji_kana_match


class DemonSoulTrad(DemonSoul):
    def __init__(self, kanaword, romajis, meanings):
        self.kanaword = kanaword
        self.romajis = romajis
        self.meanings = [meanings]

    def xp_code(self):
        return self.kanaword + ":" + (":".join(self.romajis))

    def xp_for_win(self):
        return 2

    def short_dn(self):
        return "".join(self.meanings)

    def furicode(self):
        return [("".join(self.meanings), None, False)]

    def secret_names(self):
        return self.romajis

    def meanings(self):
        return self.meanings

    def answer_ok(self, secret_name_guess):
        if romaji_kana_match(secret_name_guess, self.kanaword):
            return True
        return False

    def get_good_response(self):
        return "".join(self.kanaword)

    def hardcore_mode(self):
        return False
