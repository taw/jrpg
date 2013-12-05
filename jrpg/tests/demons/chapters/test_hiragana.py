# -*- coding: UTF-8 -*-

import unittest
from models.demons.kana.kana import DemonSoulKana
from models.demons.chapters.hiragana import Demon_chapter_hiragana


class DemonBookChapterHiraganaTest(unittest.TestCase):

    def testClassicKana(self):
        chapter = Demon_chapter_hiragana('tests/files/simplehiragana.txt')
        self.assertEquals('hiragana', chapter.get_title_of_the_chapter())
        list_of_demon = chapter.get_the_list_of_demon()
        self.assertEquals(1, len(list_of_demon))
        demon = list_of_demon[0]
        self.assertTrue(isinstance(demon, DemonSoulKana))
        self.assertEquals(demon.secret_names(), [u'da'])
    
    def testGetOneFunction(self):
        chapter = Demon_chapter_hiragana('tests/files/simplehiragana.txt')
        demon = chapter.get_one_monster('0	だ	da')
        self.assertTrue(isinstance(demon, DemonSoulKana))
        self.assertEquals(demon.secret_names(), [u'da'])

