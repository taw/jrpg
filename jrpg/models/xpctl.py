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

