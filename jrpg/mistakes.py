###########################################################
# Mistakes logger                                         #
###########################################################
import time
import codecs # Python Unicode Brain Damage

class Mistakes:
    def __init__(self):
        y,mo,d,h,mi,s,wd,yd,isdst = time.localtime()
        self.file_name = "mistakes-%04d-%02d-%02d-%02d-%02d-%02d.txt" % (y,mo,d,h,mi,s)
        self.opened = False
        self.fh = None
    def open(self):
        if not self.opened:
            self.opened = True
            self.fh = codecs.open(self.file_name, mode="ab", encoding='utf-8')
    def save_mistake(self, msg):
        try:
            self.open()
        except IOError as e:
            print e
        if self.fh:
            self.fh.write(msg)
        else:
            print msg,
    def mistake(self, attack, soul):
        msg = "Mistake: tried (%s) on demon (%s)\n" % (attack, soul.xp_code())
        self.save_mistake(msg)
