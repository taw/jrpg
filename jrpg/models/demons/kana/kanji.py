# -*- coding: UTF-8 -*-

import re
from util import ordered_uniq
from models.demons.hintengine import Hint_engine
from demonsoul import DemonSoul
from romajitokana import romaji_kana_match
from kanjifinalized import DemonSoulKanjiFinalized

from random import choice

hint = Hint_engine("data/hints-kanji.txt", "data/tanaka.txt",
"data/tanaka_idx.txt")

class DemonSoulKanji(DemonSoul):
    def __init__(self, kanji, kana, xp_for_win):
        # The last kana may be subsumed_by code actually
        if len(kana) > 0 and kana[-1][0] == '#':
            self.subsumed_by_val = int(kana[-1][1:len(kana[-1])])
            kana = kana[0:len(kana)-1]
        else:
            self.subsumed_by_val = -1                
        self.xp_for_win_val = xp_for_win

        # Most kanji demons are boring and cannot be finalized
        self.decl_code = None
        # The kanji is in kanji+kanas format,
        # that is it has more than 1 pronunciation
        if kana:
            self.xp_code_val = kanji + ":" + (":".join(kana))
            self.short_dn_val = kanji
            self.furicode_val = [(kanji, None, False)]
            self.secret_names_val = kana
            self.sub_sns_val = True
            self.tanaka_key_val = kanji
        # Kanji in single kanjicode format
        else:
            # Here's the fun
            # recode kanjicode into real_displayed_name+furicode+secret_name
            xp_code_start = kanji
            real_displayed_name = u""
            furicode            = []
            real_secret_name    = u""
            tanaka_key          = u""
            while kanji:
                m = re.match(r'^\{(.*?)\}(.*)', kanji)
                if m:
                    real_displayed_name = real_displayed_name + m.group(1)
                    furicode.append((m.group(1), None, False))
                    kanji = m.group(2)
                    continue
                m = re.match(r'^\((.*?)\|(.*?)\)(.*)', kanji)
                if m:
                    real_displayed_name = real_displayed_name + m.group(1)
                    real_secret_name    = real_secret_name    + m.group(2)
                    tanaka_key          = tanaka_key          + m.group(1)
                    furicode.append((m.group(1), m.group(2), True))
                    kanji = m.group(3)
                    continue
                m = re.match(r'^\[(.*?)\|(.*?)\](.*)', kanji)
                if m:
                    real_displayed_name = real_displayed_name + m.group(1)
                    real_secret_name    = real_secret_name    + m.group(2)
                    tanaka_key          = tanaka_key          + m.group(1)
                    furicode.append((m.group(1), m.group(2), False))
                    kanji = m.group(3)
                    continue
                m = re.match(r'^\*(.)(.*)', kanji)
                if m:
                    decl_code = m.group(1)
                    #real_displayed_name = real_displayed_name
                    #real_secret_name    = real_secret_name
                    kanji = m.group(2)
                    if m.group(2) == "5":
                        tanaka_key = tanaka_key + u"る"
                    else:
                        tanaka_key = tanaka_key + m.group(1)
                    self.decl_code = decl_code
                    if kanji: # Just test it
                        raise RuntimeError, ("Declension code *%s is not in final position" % (decl_code))
                    continue
                m = re.match(r'^(.)(.*)', kanji)
                if m:
                    real_displayed_name = real_displayed_name + m.group(1)
                    real_secret_name    = real_secret_name    + m.group(1)
                    tanaka_key          = tanaka_key          + m.group(1)
                    furicode.append((m.group(1), None, False))
                    kanji = m.group(2)
                else:
                    # This cannot happen
                    raise RuntimeError, "Internal error"
            self.xp_code_val = xp_code_start + ":" + real_secret_name
            self.short_dn_val = real_displayed_name
            self.furicode_val = furicode
            self.secret_names_val = [real_secret_name]
            self.sub_sns_val = False
            self.tanaka_key_val = tanaka_key

    def tanaka_key(self):
        return self.tanaka_key_val

    def xp_code(self):
        return self.xp_code_val

    def xp_for_win(self):
        return self.xp_for_win_val

    def short_dn(self):
        return self.short_dn_val

    def furicode(self):
        return self.furicode_val

    def secret_names(self):
        return self.secret_names_val

    def get_good_response(self):
        return self.secret_names_val

    def sub_sns(self):
        return self.sub_sns_val

    def subsumed_by(self):
        return self.subsumed_by_val

    def answer_ok(self, secret_name_guess):
        for sn in self.secret_names():
            if romaji_kana_match(secret_name_guess, sn):
                return True
        return False

    def finalize(self):
        if self.decl_code:
            decl_table = {
                u'る': [u'る', u'た', u'ない', u'ます'],
                u'5': [u'る', u'った',u'らない',u'ります'],
                u'う': [u'う', u'った', u'わない', u'います'],
                u'つ': [u'つ', u'った', u'たない', u'ちます'],
                u'く': [u'く', u'いた', u'かない', u'きます'],
                u'ぐ': [u'ぐ', u'いだ', u'がない', u'ぎます'],
                u'す': [u'す', u'した', u'さない', u'します'],
                u'む': [u'む', u'んだ', u'まない', u'みます'],
                u'ぬ': [u'ぬ', u'んだ', u'なない', u'にます'],
                u'ぶ': [u'ぶ', u'んだ', u'ばない', u'びます'],
            }
            decl = decl_table.get(self.decl_code)
            if not decl:
                raise RuntimeError, ("Declension code %s not supported" % self.decl_code)
            return(DemonSoulKanjiFinalized(self, choice(decl)))
        else:
            return self

    def get_hints(self):
        global hint
        # Use a global hint object
        return hint.get_hints(self)

    def kanji(self):
        kanji_in_demon = []
        for (kanji, furi, keep_furi) in self.furicode():
            # not furi - kana or something like that
            # keep_furi - kanji that always has furigana over it, i.e. (a|b)
            if (not furi) or keep_furi:
                continue
            # To deal with irregular words like otona
            for kanji_char in kanji:
                kanji_in_demon.append(kanji_char)
        return ordered_uniq(kanji_in_demon)

    def hardcore_mode(self):
        return False

