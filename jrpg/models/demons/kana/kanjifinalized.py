from demonsoul import DemonSoul
from romajitokana import romaji_kana_match


# Aux class, do not call except from DemonSoulKanji#finalize()
class DemonSoulKanjiFinalized(DemonSoul):
    def __init__(self, root, ending):
        self.root = root
        self.ending = ending

    def tanaka_key(self):
        return self.root.tanaka_key()

    def xp_code(self):
        return self.root.xp_code()

    def xp_for_win(self):
        return self.root.xp_for_win()

    def short_dn(self):
        return self.root.short_dn() + self.ending

    def furicode(self):
        # There will be only one but anyway
        return self.root.furicode() + [(self.ending, None, False)]

    def secret_names(self):
        return [x+self.ending for x in self.root.secret_names()]

    def sub_sns(self):
        return self.root.sub_sns()

    def subsumed_by(self):
        return self.root.subsumed_by()

    def answer_ok(self, secret_name_guess):
        for sn in self.secret_names():
            if romaji_kana_match(secret_name_guess, sn):
                return True
        return False

    def get_hints(self):
        return self.root.get_hints()

    def hardcore_mode(self):
        return True
    # No def finalize(self), one cannot refinalize the demon
