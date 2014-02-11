#!/usr/bin/python
# -*- coding: UTF-8 -*-

from random import choice
from util import ordered_uniq


###########################################################
# This class selects hints for demons that hit you        #
###########################################################
class Hint_engine:
    # Structure:
    # self.compound - key is "kanji:furi" or "kanji:*"
    #                 data is hint
    # self.tanaka_idx - key is word
    #                   data is array of line indices into Tanaka corpus
    # self.tanaka_file - file handler of Tanaka corpus
    def __init__(self, hints_kanji_filename, tanaka_corpus_filename,
            tanaka_index_filename):
        self.compound = {}
        f = open(hints_kanji_filename)
        for line in f.readlines():
            key, reading, meaning = unicode(line, "UTF-8").strip(U"\n").split(U"\t")
            self.compound[key] = reading + u" " + meaning
        f.close()

        self.tanaka_idx = {}
        self.tanaka_file = open(tanaka_corpus_filename)

        f = open(tanaka_index_filename)
        for line in f.readlines():
            fields = unicode(line, "UTF-8").strip(U"\n").split(U"\t")
            (key, idx) = (fields[0], fields[1:len(fields)])
            self.tanaka_idx[key] = [int(x) for x in idx]
        f.close()

    def tanaka_get(self, idx):
        self.tanaka_file.seek(idx)
        return unicode(self.tanaka_file.readline(), "UTF-8").strip(U"\n")

    def get_random_tanaka(self, key):
        candidates = self.tanaka_idx.get(key, [])
        if candidates:
            tanaka = self.tanaka_get(choice(candidates))
            jp, en = tanaka.split("\t")
            # tanaka has format JP\tEN
            # We can do a word wrap here
            # * First, try packing everything in one line
            # * If it doesn't work, try JP first line, EN second line
            # * If it doesn't work either, try word-wrap (at any character)
            # Only the first 2 options are implemented
            jp_len = len(jp)
            en_len = len(en)
            #print [jp_len, en_len, 2*jp_len+en_len, tanaka]
            if 2*jp_len+en_len <= 66:
                return [jp + en]
            else:
                return [jp, en]
        else:
            return []
    def get_hints(self, demon):
        tanaka_hint = self.get_random_tanaka(demon.tanaka_key())

        kanji_hints = []
        for (kanji, furi, kf) in demon.furicode():
            if not furi:
                continue
            hint = self.compound.get(kanji + u":" + furi)
            if not hint:
                hint = self.compound.get(kanji + u":*")
            if hint:
                kanji_hints.append(hint)
            # If the word is irregular, still try to extract the meaning of some fragments
            elif len(kanji) > 1:
                for hint in map(lambda kanji_char: self.compound.get(kanji_char + u":*"), kanji):
                    if hint:
                        kanji_hints.append(hint)
        # Let's assume the first ones will be displayed in case of overflow
        hints = []
        if tanaka_hint: hints = hints + tanaka_hint
        if kanji_hints: hints = hints + ordered_uniq(kanji_hints)
        
        if hints:
            return hints # If there are more than 3 we have a problem
        else:
            return []

