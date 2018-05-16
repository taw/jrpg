# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from .demonsoul import DemonSoul


class DemonSoulKana(DemonSoul):
    def __init__(self, kana, romajis):
        self.kana = kana
        self.romajis = romajis

    def xp_code(self):
        return self.kana + ":" + (":".join(self.romajis))

    def xp_for_win(self):
        return 1

    def short_dn(self):
        return self.kana

    def furicode(self):
        return [(self.kana, None, False)]

    def secret_names(self):
        return self.romajis

    def get_good_response(self):
        return self.romajis

    def answer_ok(self, secret_name_guess):
        if secret_name_guess in self.romajis:
            return True
        return False

    def hardcore_mode(self):
        return True
