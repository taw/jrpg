# -*- coding: UTF-8 -*-

from .chapter import DemonBookChapter
from models.demons.kana.trad import DemonSoulTrad


# Class for load the traduction kanaword
# the code is almost the same of demonBookChapterKanaWord
class DemonChapterTrad(DemonBookChapter):
    def __init__(self, filename):
        """constructor
        """
        DemonBookChapter.__init__(self, filename)
        self.name = "traduction"

    def get_one_monster(self, line):
        """the method to read one line of the file
        the format here 'hiragana<tab>romaji ..<tab> meaning'
        we use the same file un DemonBookChapterKanaword
        """
        fields = line.strip("\n").split("\t")
        kana, romajis, meanings = (fields[0],
                                   fields[1:len(fields)-1], fields[-1])
        return DemonSoulTrad(kana, romajis, meanings)
