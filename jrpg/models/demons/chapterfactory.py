from models.demons.chapters.katakana import Demon_chapter_katakana
from models.demons.chapters.hiragana import Demon_chapter_hiragana
from models.demons.chapters.kanaword import Demon_chapter_kanaword
from models.demons.chapters.trad import Demon_chapter_trad
from models.demons.chapters.kanji import Demon_chapter_kanji


class Chapter_factory:
    # Pseudo factory method
    # TODO create a specific class ?
    # there is probably a python "way" to do it
    def get_chapter_for_book_of_demon(self, type, filename):
        if type == 'katakana':
            return Demon_chapter_katakana(filename)
        elif type == 'hiragana':
            return Demon_chapter_hiragana(filename)
        elif type == 'kanaword':
            return Demon_chapter_kanaword(filename)
        elif type == 'traduction':
            return Demon_chapter_trad(filename)
        elif type == 'kanji':
            return Demon_chapter_kanji(filename)
