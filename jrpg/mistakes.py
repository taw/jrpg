###########################################################
# Mistakes logger                                         #
###########################################################
import time
import codecs # Python Unicode Brain Damage

class Mistakes:
    def __init__(self):
        y,mo,d,h,mi,s,wd,yd,isdst = time.localtime()
        self.file_name = "mistakes-%04d-%02d-%02d-%02d-%02d-%02d.txt" % (y,mo,d,h,mi,s)
        self.fh = None
    def open(self):
        if not self.fh:
            self.fh = codecs.open(self.file_name, mode="ab", encoding='utf-8')
    def mistake(self, attack, soul):
        msg = "Mistake: tried (%s) on demon (%s)\n" % (attack, soul.xp_code())
        self.open()
        self.fh.write(msg)
