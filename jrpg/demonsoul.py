#!/usr/bin/python
# -*- coding: UTF-8 -*-

import re
import warnings
from random import choice

# Import other jrpg modules
from kana import romaji_kana_match
from util import ordered_uniq

# In hardcore mode the demon doesn't tell its name
# on the first encounter, it attacks straight away
hardcore_kana     = True
hardcore_kanaword = True
hardcore_kanji    = False
hardcore_trad     = False

###########################################################
# Class for managing xp                                   #
###########################################################
class XpCtl:
    def __init__(self, data=None):
        if not data:
            data = {}
        self.xpfor = data
    def dump(self):
        return self.xpfor
    
    #def seen_key(self, key):
    #    return self.xpfor.get(key, -1) != -1
    def seen_soul(self, soul):
        return (soul.hardcore_mode() or self.xpfor.get(soul.xp_code(), -1) != -1)

    def beaten(self, key):
        return self.xpfor.get(key, 0) >= 1
    def maxed(self, key):
        return self.xpfor.get(key, 0) == 3
    def see(self, key):
        current_xp = self.xpfor.get(key, 0)
        self.xpfor[key] = current_xp
    # return True if got any xp
    def beat(self, key):
        current_xp = self.xpfor.get(key, 0)
        new_xp = min(current_xp+1, 3)
        self.xpfor[key] = new_xp
        return (current_xp != new_xp)
    # return True if got any xp
    
    #def see_or_beat_key(self, key):
    #    if self.seen_key(key):
    #        return self.beat(key)
    #    else:
    #        self.see(key)
    #        return False
    def see_or_beat_soul(self, soul):
        if self.seen_soul(soul):
            return self.beat(soul.xp_code())
        else:
            self.see(soul.xp_code())
            return False
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
    def __init__(self):
        self.compound = {}
        f = open("data/hints-kanji.txt")
        for line in f.readlines():
            (key, reading, meaning) = unicode(line, "UTF-8").strip(U"\n").split(U"\t")
            self.compound[key] = reading + u" " + meaning
        f.close()

        self.tanaka_idx = {}
        self.tanaka_file = open("data/tanaka.txt")

        f = open("data/tanaka_idx.txt")
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
        for (kanji,furi,kf) in demon.furicode():
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

###########################################################
# These classes implement souls of the demons             #
###########################################################

# Demons are instances of class DemonSoul*
# Methods are:
# xp_code      : string
# short_dn     : string
# furicode     : furicode
# secret_names : string list
# sub_sns      : bool
# subsumed_by  : int (index of element inside a class or -1 for None)
# finalize     : demon # perform random finalization, if any
# check_answer : string -> bool
class DemonSoul:
    pass
    # The following will be overloaded in every subclass anyway:
    # def xp_code
    # def xp_for_win
    # def short_dn
    # def furicode
    # def secret_names
    # def answer_ok
    # def hardcore_mode
    
    def tanaka_key(self):
        return None
    
    def sub_sns(self): # should we display secret names below the kanji when it's first seen ?
        return True
    
    def subsumed_by(self):
        return -1
    
    def finalize(self):
        return self
    
    def get_hints(self):
        return None
    
    def get_success_message(self): 
        return U"You slayed demon %s (%s)." % (
                self.short_dn(),
                " ".join(self.secret_names())
        )

    def get_fail_message(self, damage): 
        return U"Demon %s (%s) hit you for %d points" % ( self.short_dn(),
                "".join(self.secret_names()), damage)

    def __unicode__(self):
        return self.xp_code()



class DemonSoulKana(DemonSoul):
    def __init__(self, kana, romajis):
        self.kana = kana
        self.romajis = romajis
    def xp_code(self):
        return self.kana + ":" + (":".join(self.romajis))
    def xp_for_win(self):
        return 1
    def short_dn(self):
        return self.kana
    def furicode(self):
        return [(self.kana, None, False)]
    def secret_names(self):
        return self.romajis
    def get_good_response(self):
        return self.romajis

    def answer_ok(self, secret_name_guess):
        if secret_name_guess in self.romajis:
            return True
        return False
    
    def hardcore_mode(self):
        return hardcore_kana


class DemonSoulKanaword(DemonSoul):
    def __init__(self, kanaword, romajis, meanings):
        self.kanaword = kanaword
        self.romajis = romajis
        self.meanings = [meanings]
        # Some wishful thinking:
        #kunrei = canonical_kunrei(displayed_name)
        #hepburn = canonical_hepburn(displayed_name)
        #if kunrei == hepburn:
        #    self.romajis = [kunrei]
        #else:
        #    self.romajis = [kunrei, hepburn]
    def xp_code(self):
        return self.kanaword + ":" + (":".join(self.romajis))
    def xp_for_win(self):
        return 2
    def short_dn(self):
        return self.kanaword
    def furicode(self):
        return [(self.kanaword, None, False)]
    def secret_names(self):
        return self.romajis
    def meanings(self):
        return self.meanings
    def answer_ok(self, secret_name_guess):
        if romaji_kana_match(secret_name_guess, self.kanaword):
            return True
        return False
    def get_good_response(self):
        return self.romajis
    def hardcore_mode(self):
        return hardcore_kanaword

class DemonSoulTrad(DemonSoul):
    def __init__(self, kanaword, romajis, meanings):
        self.kanaword = kanaword
        self.romajis = romajis
        self.meanings = [meanings]
        # Some wishful thinking:
        #kunrei = canonical_kunrei(displayed_name)
        #hepburn = canonical_hepburn(displayed_name)
        #if kunrei == hepburn:
        #    self.romajis = [kunrei]
        #else:
        #    self.romajis = [kunrei, hepburn]
    def xp_code(self):
        return self.kanaword + ":" + (":".join(self.romajis))
    def xp_for_win(self):
        return 2
    def short_dn(self):
        return "".join(self.meanings);
    def furicode(self):
        return [("".join(self.meanings), None, False)]
    def secret_names(self):
        return self.romajis
    def meanings(self):
        return self.meanings
    def answer_ok(self, secret_name_guess):
        if romaji_kana_match(secret_name_guess, self.kanaword):
            return True
        return False
    
    def get_good_response(self):
        return "".join(self.kanaword)
    
    def hardcore_mode(self):
        return hardcore_trad

class DemonSoulKanji(DemonSoul):
    def __init__(self, kanji, kana, xp_for_win):
        # The last kana may be subsumed_by code actually
        if len(kana) > 0 and kana[-1][0] == '#':
            self.subsumed_by_val = int(kana[-1][1:len(kana[-1])])
            kana = kana[0:len(kana)-1]
        else:
            self.subsumed_by_val = -1                
        self.xp_for_win_val = xp_for_win

        # Most kanji demons are boring and cannot be finalized
        self.decl_code = None
        # The kanji is in kanji+kanas format,
        # that is it has more than 1 pronunciation
        if kana:
            self.xp_code_val = kanji + ":" + (":".join(kana))
            self.short_dn_val = kanji
            self.furicode_val = [(kanji, None, False)]
            self.secret_names_val = kana
            self.sub_sns_val = True
            self.tanaka_key_val = kanji
        # Kanji in single kanjicode format
        else:
            # Here's the fun
            # recode kanjicode into real_displayed_name+furicode+secret_name
            xp_code_start = kanji
            real_displayed_name = u""
            furicode            = []
            real_secret_name    = u""
            tanaka_key          = u""
            while kanji:
                m = re.match(r'^\{(.*?)\}(.*)', kanji)
                if m:
                    real_displayed_name = real_displayed_name + m.group(1)
                    furicode.append((m.group(1), None, False))
                    kanji = m.group(2)
                    continue
                m = re.match(r'^\((.*?)\|(.*?)\)(.*)', kanji)
                if m:
                    real_displayed_name = real_displayed_name + m.group(1)
                    real_secret_name    = real_secret_name    + m.group(2)
                    tanaka_key          = tanaka_key          + m.group(1)
                    furicode.append((m.group(1), m.group(2), True))
                    kanji = m.group(3)
                    continue
                m = re.match(r'^\[(.*?)\|(.*?)\](.*)', kanji)
                if m:
                    real_displayed_name = real_displayed_name + m.group(1)
                    real_secret_name    = real_secret_name    + m.group(2)
                    tanaka_key          = tanaka_key          + m.group(1)
                    furicode.append((m.group(1), m.group(2), False))
                    kanji = m.group(3)
                    continue
                m = re.match(r'^\*(.)(.*)', kanji)
                if m:
                    decl_code = m.group(1)
                    #real_displayed_name = real_displayed_name
                    #real_secret_name    = real_secret_name
                    kanji = m.group(2)
                    if m.group(2) == "5":
                        tanaka_key = tanaka_key + u"る"
                    else:
                        tanaka_key = tanaka_key + m.group(1)
                    self.decl_code = decl_code
                    if kanji: # Just test it
                        raise RuntimeError, ("Declension code *%s is not in final position" % (decl_code))
                    continue
                m = re.match(r'^(.)(.*)', kanji)
                if m:
                    real_displayed_name = real_displayed_name + m.group(1)
                    real_secret_name    = real_secret_name    + m.group(1)
                    tanaka_key          = tanaka_key          + m.group(1)
                    furicode.append((m.group(1), None, False))
                    kanji = m.group(2)
                else:
                    # This cannot happen
                    raise RuntimeError, "Internal error"
            self.xp_code_val = xp_code_start + ":" + real_secret_name
            self.short_dn_val = real_displayed_name
            self.furicode_val = furicode
            self.secret_names_val = [real_secret_name]
            self.sub_sns_val = False
            self.tanaka_key_val = tanaka_key
    def tanaka_key(self):
        return self.tanaka_key_val
    def xp_code(self):
        return self.xp_code_val
    def xp_for_win(self):
        return self.xp_for_win_val
    def short_dn(self):
        return self.short_dn_val
    def furicode(self):
        return self.furicode_val
    def secret_names(self):
        return self.secret_names_val
    def get_good_response(self):
        return self.secret_names_val

    def sub_sns(self):
        return self.sub_sns_val
    def subsumed_by(self):
        return self.subsumed_by_val
    def answer_ok(self, secret_name_guess):
        for sn in self.secret_names():
            if romaji_kana_match(secret_name_guess, sn):
                return True
        return False
    def finalize(self):
        if self.decl_code:
            decl_table = {
                u'る' : [u'る', u'た', u'ない', u'ます'],
                u'5' : [u'る', u'った',u'らない',u'ります'],
                u'う' : [u'う', u'った', u'わない', u'います'],
                u'つ' : [u'つ', u'った', u'たない', u'ちます'],
                u'く' : [u'く', u'いた', u'かない', u'きます'],
                u'ぐ' : [u'ぐ', u'いだ', u'がない', u'ぎます'],
                u'す' : [u'す', u'した', u'さない', u'します'],
                u'む' : [u'む', u'んだ', u'まない', u'みます'],
                u'ぬ' : [u'ぬ', u'んだ', u'なない', u'にます'],
                u'ぶ' : [u'ぶ', u'んだ', u'ばない', u'びます'],
            }
            decl = decl_table.get(self.decl_code)
            if not decl:
                raise RuntimeError, ("Declension code %s not supported" % self.decl_code)
            return(DemonSoulKanjiFinalized(self, choice(decl)))
        else:
            return self
    def get_hints(self):
        # Use a global hint object
        return hint.get_hints(self)
    def kanji(self):
        kanji_in_demon = []
        for (kanji,furi,keep_furi) in self.furicode():
            # not furi - kana or something like that
            # keep_furi - kanji that always has furigana over it, i.e. (a|b)
            if (not furi) or keep_furi:
                continue
            # To deal with irregular words like otona
            for kanji_char in kanji:
                kanji_in_demon.append(kanji_char)
        return ordered_uniq(kanji_in_demon)
    def hardcore_mode(self):
        return hardcore_kanji

# Aux class, do not call except from DemonSoulKanji#finalize()
class DemonSoulKanjiFinalized(DemonSoul):
    def __init__(self, root, ending):
        self.root = root
        self.ending = ending
    def tanaka_key(self):
        return self.root.tanaka_key()
    def xp_code(self):
        return self.root.xp_code()
    def xp_for_win(self):
        return self.root.xp_for_win()
    def short_dn(self):
        return self.root.short_dn() + self.ending
    def furicode(self):
        # There will be only one but anyway
        return self.root.furicode() + [(self.ending, None, False)]
    def secret_names(self):
        return [x+self.ending for x in self.root.secret_names()]
    def sub_sns(self):
        return self.root.sub_sns()
    def subsumed_by(self):
        return self.root.subsumed_by()
    def answer_ok(self, secret_name_guess):
        for sn in self.secret_names():
            if romaji_kana_match(secret_name_guess, sn):
                return True
        return False
    def get_hints(self):
        return self.root.get_hints()
    def hardcore_mode(self):
        return hardcore_kanji
    # No def finalize(self), one cannot refinalize the demon
###########################################################
# This class manages the book of demons                   #
###########################################################
# Classes:
# 0 - hiragana
# 1 - katakana
# 2 - kana words
# 3 - Kanji demons
# Classes at locations:
# 0                 @ Dark forest
# 0+1               @ Dwarven hills
# 0+1+2             @ Mushroom forest
# 2+3                    @ Desert
# 2+3               @ Tower
# 3                 @ Icy mountains
# 3                 @ Dungeon
class Book_of_demons:
    def __init__(self):
        self.demons = {}

        f = open("data/demons-kana.txt")
        lines = f.readlines()
        f.close()
        for line in lines:
            fields = unicode(line, "UTF-8").strip(U"\n").split(U"\t")
            (demon_class, kana, romajis) = (int(fields[0]), fields[1], fields[2:len(fields)])
            if not self.demons.has_key(demon_class):
                self.demons[demon_class] = []
            d = DemonSoulKana(kana, romajis)
            self.demons[demon_class].append(d)

        self.demons[2] = []
        self.demons[4] = []
        f = open("data/demons-kanawords.txt")
        lines = f.readlines()
        f.close()
        for line in lines:
            fields = unicode(line, "UTF-8").strip(U"\n").split(U"\t")
            (kana, romajis, meanings) = (fields[0],
                    fields[1:len(fields)-1],fields[-1])
            d = DemonSoulKanaword(kana, romajis, meanings)
            self.demons[2].append(d)
            d = DemonSoulTrad(kana, romajis, meanings)
            self.demons[4].append(d)

        f = open("data/demons-kanji.txt")
        lines = f.readlines()
        f.close()
        
        i = 0
        for line in lines:
            fields = unicode(line, "UTF-8").strip(U"\n").split(U"\t")
            (demon_class, kanji) = (int(fields[0]), fields[1])
            kana = fields[2:len(fields)]
            xp_for_win = 3 + (i / 500)
            d = DemonSoulKanji(kanji, kana, xp_for_win)
            if not self.demons.has_key(demon_class):
                self.demons[demon_class] = []
            self.demons[demon_class].append(d)
            i = i + 1
        
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
            if type(demon_class) == int:
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
                if demon_class != 3:
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

    def get_one(self, xpctl, demon_classes):
        candidates = []
        for demon_class in demon_classes:
            if type(demon_class) == int:
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
                if demon_class != 3:
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

###########################################################
# Module-globals                                          #
###########################################################
hint = Hint_engine()
