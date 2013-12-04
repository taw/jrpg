#!/usr/bin/python
# -*- coding: UTF-8 -*-

from chapter import DemonBookChapter
from models.demons.kana.kanaword import DemonSoulKanaword


# Class for load the complete kana work
# in the book of demons
class Demon_chapter_kanaword(DemonBookChapter):
    def __init__(self, filename):
        '''constructor
        '''
        DemonBookChapter.__init__(self, filename)
        self.name = 'kanaword'

    def get_one_monster(self, line):
        '''the method to read one line of the file
        the format here 'hiragana<tab>romanji ..<tab>meaning'
        '''
        fields = unicode(line, "UTF-8").strip(U"\n").split(U"\t")

        kana, romajis, meanings = (fields[0], fields[1:len(fields)-1], fields[-1])

        return DemonSoulKanaword(kana, romajis, meanings)
