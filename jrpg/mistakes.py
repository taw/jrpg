###########################################################
# Mistakes logger                                         #
###########################################################
import time
import codecs # Python Unicode Brain Damage


# In this otherwise completely straightforward 3-line class
# we have to deal with Python's Unicode Brain Damage
class Mistakes:
    def __init__(self):
        y,mo,d,h,mi,s,wd,yd,isdst = time.localtime()
        fn = "mistakes-%04d-%02d-%02d-%02d-%02d-%02d.txt" % (y,mo,d,h,mi,s)
        #self.fh = open(fn, "ab")
        self.fh = codecs.open(fn, mode="ab", encoding='utf-8')
    def mistake(self, attack, soul):
        msg = "Mistake: tried (%s) on demon (%s)\n" % (attack, soul.xp_code())
        self.fh.write(msg)


