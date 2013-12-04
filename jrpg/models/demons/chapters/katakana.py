# -*- coding: UTF-8 -*-

from chapter import DemonBookChapter
from models.demons.kana.kana import DemonSoulKana

# Class for load the katakana
# in the book of demons
# The code is almost the same than DemonBookChapterHiragana
class Demon_chapter_katakana(DemonBookChapter):
    
    def __init__(self, filename):
        DemonBookChapter.__init__(self, filename)
        self.name = 'katakana'

    def get_one_monster(self, line):
        ''' 
        the method to read one line of the file
        the format here 'demon_class<tab>katakana<tab>romanji ..<tab>'
        the demon_class is not usefull for us
        '''
        fields = unicode(line, "UTF-8").strip(U"\n").split(U"\t")
        (demon_class, kana, romajis) = (int(fields[0]), fields[1], fields[2:len(fields)])
        return DemonSoulKana(kana, romajis)

