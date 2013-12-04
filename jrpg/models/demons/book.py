from models.demons.chapters.katakana import Demon_chapter_katakana
from models.demons.chapters.hiragana import Demon_chapter_hiragana
from models.demons.chapters.kanaword import Demon_chapter_kanaword
from models.demons.chapters.trad import Demon_chapter_trad
from models.demons.chapters.kanji import Demon_chapter_kanji

from random import choice

###########################################################
# This class manages the book of demons                   #
###########################################################
# Classes:
# Classes at locations:
# "hiragana"              @ Dark forest
# "hiragana" + "katakana" @ Dwarven hills
# "hiragana" + "katakana"+"kanaword"+"traduction" @ Mushroom forest
# "kanaword" + "kanji"    @ Desert
# "kanaword" + "kanji"    @ Tower
# "kanji"                 @ Icy mountains
# "kanji"                 @ Dungeon

class Book_of_demons:
    def add_chapter_to_the_book(self, chapter):
        self.demons[chapter.get_title_of_the_chapter()] = []
        self.demons[chapter.get_title_of_the_chapter()] = chapter.get_the_list_of_demon()

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

    def __init__(self, config={}):
        self.demons = {}
        # TODO give a dictionnary {'katakana': 'data/demonkatakana.txt' ..}.
        # and do a foreach in this dictionnary
        self.add_chapter_to_the_book(
                self.get_chapter_for_book_of_demon(
                    'katakana',
                    'data/demons-katakana.txt'))
        self.add_chapter_to_the_book(self.get_chapter_for_book_of_demon('hiragana',
            'data/demons-hiragana.txt'))
        self.add_chapter_to_the_book(self.get_chapter_for_book_of_demon('kanaword',
            'data/demons-kanawords.txt'))
        self.add_chapter_to_the_book(self.get_chapter_for_book_of_demon('traduction',
            'data/demons-kanawords.txt'))
        self.add_chapter_to_the_book(self.get_chapter_for_book_of_demon('kanji',
            'data/demons-kanji.txt'))

        #Debug:
        #for chapter_id in self.demons:
        #    for d in self.demons[chapter_id]:
        #        print (u"%s" % d)
    # demon_class is a list of classes. Each class is either of:
    # 0       - everything in class 0 (or 1,2,3)
    # (3,100) - just enough demons in class 3 to have a least 100 undefeated (for some values of 100)
    # Class 3 (Kanji demons)
    #
    # Change to use XpCtl
    def choice(self, xpctl, sample_size, demon_classes):
        unbeaten = []
        weighted_demon_list = []
        for demon_class in demon_classes:
            # For kana/kanaword classes use probabilities:
            # 1 - maxed
            # 2 - not maxed
            if isinstance(demon_class, basestring):  #is
                for demon in self.demons[demon_class]:
                    if xpctl.maxed(demon.xp_code()):
                        w = 1
                    else:
                        w = 2
                    weighted_demon_list.append((demon, w))
            else:
                # There should always be demons_limit (like 300) unbeaten (None or 0) demons,
                # if that's possible at all
                #
                # Use probabilities:
                # 0 - maxed and the subsumed demon beaten
                # 1 - maxed
                # 2 - beaten
                # 8..2 - unbeaten
                demon_class, demons_limit = demon_class
                demons_undefeated = 0
                if demon_class != 'kanji':
                    # It will work, but there are no such other classes as for now
                    raise "Demon class limit applied to class different than Kanji demons"
                demons = self.demons[demon_class]
                for demon in demons:
                    # It's possible that we remove subsumed demon while the subsuming one
                    # is not included. For example, if Y subsumes X:
                    # (X) [150 unbeaten demons] [Y]
                    # On level 2 (demons_limit=200): (X not included) [150 unbeaten demons] [Y] [49 demons]
                    # * Correct
                    # On level 1 (demons_limit=100): (X not included) [100 unbeaten demons]
                    # * Not cool, but not fatal
                    if xpctl.maxed(demon.xp_code()):
                        if (demon.subsumed_by() != -1 and
                            xpctl.beaten(demons[demon.subsumed_by()].xp_code())):
                            continue
                        else:
                            weighted_demon_list.append((demon, 1))
                    elif xpctl.beaten(demon.xp_code()):
                        weighted_demon_list.append((demon, 2))
                    else:
                        unbeaten.append(demon)
                        demons_undefeated += 1
                        if (demons_undefeated == demons_limit):
                            break
                # Assign probabilities from 8 to 2 to unbeaten demons
                # This lowers the chance that easy demon will be unmet
                for i in range(len(unbeaten)):
                    w = 8 - (8-1)*i/len(unbeaten)
                    weighted_demon_list.append((unbeaten[i], w))

        #for (d, w) in weighted_demon_list:
        #    print "%d: %s" % (w, d.xp_code())
        return [x.finalize() for x in weighted_sample(weighted_demon_list, sample_size)]

    # Useless Not called ?
    def get_one(self, xpctl, demon_classes):
        candidates = []
        for demon_class in demon_classes:
            if  demon_class != 'kanji':
                for demon in self.demons[demon_class]:
                    # maxed demons twice less probable
                    if not xpctl.maxed(demon.xp_code()):
                        candidates.append(demon)
                    candidates.append(demon)
            else:
                # There should always be demons_limit (like 300) unbeaten demons,
                # if that's possible at all
                demon_class, demons_limit = demon_class
                demons_undefeated = 0
                if demon_class != 'kanji':
                    # It will work, but there are no such other classes as for now
                    raise "Demon class limit applied to class different than Kanji demons"
                demons = self.demons[demon_class]
                for demon in demons:
                    # It's possible that we remove subsumed demon while the subsuming one
                    # is not included. For example, if Y subsumes X:
                    # (X) [150 unbeaten demons] [Y]
                    # On level 2 (demons_limit=200): (X not included) [150 unbeaten demons] [Y] [49 demons]
                    # * Correct
                    # On level 1 (demons_limit=100): (X not included) [100 unbeaten demons]
                    # * Not cool, but not fatal
                    if not xpctl.maxed(demon.xp_code()):
                        candidates.append(demon)
                    else:
                        if (demon.subsumed_by() != -1 and
                            xpctl.beaten(demons[demon.subsumed_by()].xp_code())):
                            continue
                    candidates.append(demon)

                    if not xpctl.beaten(demon):
                        demons_undefeated += 1
                    if (demons_undefeated == demons_limit):
                        break
        return choice(candidates).finalize()

# population is (x, weight of x) list
# select random sample of different elements
# weight should be a *SMALL* *POSITIVE* INTEGER
# The function is AWFULLY INEFFICIENT,
# but reasonably sane
def weighted_sample(population, sample_size):

    if len(population) < sample_size:
        raise ("weighted_sample: size of population %d is smaller than sample size %d" % (len(population), sample_size))
    balls = {}
    start_cnt = []
    # Put weight_x balls numbered from start_cnt[i] to start_cnt[i]+population[i][1]-1 in the container
    j = 0
    sample = []
    for i in range(len(population)):
        start_cnt.append(j)
        for k in range(population[i][1]):
            balls[j] = i
            j += 1
    for i in range(sample_size):
        object_id = balls[choice(balls.keys())]
        # Remove all balls of the selected object
        for k in range(start_cnt[object_id], start_cnt[object_id]+population[object_id][1]):
            del balls[k]
        sample.append(population[object_id][0])
    return sample

