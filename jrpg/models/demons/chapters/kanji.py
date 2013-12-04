# -*- coding: UTF-8 -*-

from chapter import DemonBookChapter
from models.demons.kana.kanji import DemonSoulKanji


# Class for load the Kanji
class Demon_chapter_kanji(DemonBookChapter):
    def __init__(self, filename):
        self.demons = []
        self.name = 'kanji'
        f = open(filename)
        lines = f.readlines()
        f.close()

        i = 0
        for line in lines:
            fields = unicode(line, "UTF-8").strip(U"\n").split(U"\t")
            (demON_CLASS, kanji) = (int(fields[0]), fields[1])
            kana = fields[2:len(fields)]
            xp_for_win = 3 + (i / 500)
            d = DemonSoulKanji(kanji, kana, xp_for_win)
            self.demons.append(d)
            i = i + 1
