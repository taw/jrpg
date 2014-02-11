# -*- coding: UTF-8 -*-


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

    def sub_sns(self):  # should we display secret names
                        # below the kanji when it's first seen ?
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
        return U"Demon %s (%s) hit you for %d points" % (
               self.short_dn(),
               " ".join(self.secret_names()), damage)

    def __unicode__(self):
        return self.xp_code()
