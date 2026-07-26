from models.demons.chapters.katakana import DemonChapterKatakana
from models.demons.chapters.hiragana import DemonChapterHiragana
from models.demons.chapters.kanaword import DemonChapterKanaword
from models.demons.chapters.trad import DemonChapterTrad
from models.demons.chapters.kanji import DemonChapterKanji


class ChapterFactory:
    # Pseudo factory method
    # TODO create a specific class ?
    # there is probably a python "way" to do it
    def get_chapter_for_book_of_demon(self, type, filename):
        if type == "katakana":
            return DemonChapterKatakana(filename)
        elif type == "hiragana":
            return DemonChapterHiragana(filename)
        elif type == "kanaword":
            return DemonChapterKanaword(filename)
        elif type == "traduction":
            return DemonChapterTrad(filename)
        elif type == "kanji":
            return DemonChapterKanji(filename)
