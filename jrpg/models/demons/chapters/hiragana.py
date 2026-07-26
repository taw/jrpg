# -*- coding: UTF-8 -*-

from .chapter import DemonBookChapter
from models.demons.kana.kana import DemonSoulKana


# Class for load the Hiragana
# in the book of demons
class DemonChapterHiragana(DemonBookChapter):
    def __init__(self, filename):
        """same as the abstract class"""
        DemonBookChapter.__init__(self, filename)
        """the name of the type"""
        self.name = "hiragana"

    def get_one_monster(self, line):
        """the method to read one line of the file
        the format here 'demon_class<tab>hiragana<tab>romaji ..<tab>'
        the demon_class is not useful for us
        """
        fields = line.strip("\n").split("\t")
        demon_class, kana, romajis = int(fields[0]), fields[1], fields[2:len(fields)]
        return DemonSoulKana(kana, romajis)
