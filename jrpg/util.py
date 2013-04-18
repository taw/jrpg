#!/usr/bin/python
# -*- coding: UTF-8 -*-

# A file for small functions common to JRPG and JRPG 2

import pygame
import traceback
import time

try:
    import posix
    posix_present = True
except ImportError:
    posix_present = False

###########################################################
# Where to look for the font                              #
###########################################################
# This is the list of checked paths
# If the font file is somewhere else, add its full path to the list
# This is complicated because we want it to work with posix present and without it
# Full paths
# Actually it's much easier to simply include the font in jrpg :-)
full_font_paths = [
    "font/kochi-gothic.ttf", # This is the official location
    "/usr/share/fonts/truetype/kochi/kochi-gothic.ttf", # Standard directory on Debian and Ubuntu
    "/usr/share/fonts/kochi-substitute/kochi-gothic-subst.ttf", # Gentoo
    "c:/windows/fonts/kochi-gothic.ttf", # Some sane location under Windows
    # "/your/directory/kochi-gothic.ttf", # Path to your font
]
# What to look for in $HOME or the current directory
font_file_names = [
    "kochi-gothic.ttf",
    "kochi-gothic-subst.ttf",
]

############################################################
# This class manages notifications                         #
# It's used mostly together with Cached object             #
############################################################
class Notifier:
    def __init__(self):
        self.listeners = []
    def fire(self):
        for listener in self.listeners:
            listener()
    def register(self, listener):
        self.listeners.append(listener)

############################################################
# This class manages cached computations                   #
# Cached object are typically connected to a notifier      #
############################################################
class Cached:
    def __init__(self, function, listen=None):
        self.valid = False
        self.function = function
        if listen:
            listen.register(lambda: self.invalidate())
    def invalidate(self):
        self.valid = False
    def execute(self):
        if not self.valid:
            self.function()
            self.valid = True

###########################################################
# Font loading function                                   #
###########################################################
def load_font(*sizes):
    font_paths = font_file_names # Search current directory first
    if posix_present:
        dot_fonts = posix.environ["HOME"] + "/.fonts/"
        font_paths = font_paths + [(dot_fonts + font_file_name) for font_file_name in font_file_names]
    font_paths = font_paths + full_font_paths

    error_msg = ""
    for font_path in font_paths:
        try:
            return [pygame.font.Font(font_path, size) for size in sizes]
        except IOError, e:
            error_msg += "Opening font at %s failed: %s\n" % (font_path, e)
    raise error_msg

def init_pygame(window_title):
    # Calling pygame.init() initialized funny things like cdrom playing too
    # It's not a good idea
    pygame.display.init()
    pygame.display.set_caption(window_title)
    pygame.font.init()

def sgn(x):
    if x > 0:
        return +1
    elif x == 0:
        return 0
    else:
        return -1
    
def save_errormsg(trace_back):
    (tp,v,tb) = trace_back
    tbf = traceback.format_exception(tp,v,tb)
    f = open("errormsg.txt", "a")
    f.write("== ")
    f.write(time.asctime(time.localtime()))
    f.write(" ==\n")
    for line in tbf:
        f.write(line)
    f.write("\n")
    f.close()

# Remove duplicates from lst, leaving only the first
# occurence of each value
def ordered_uniq(lst):
    res = []
    for el in lst:
        if not (el in res):
            res.append(el)
    return res

# It is really annoying to have .sort() sort in-place instead of
# returning a sorted list. They *could* have fixed it when
# switching from procedural to OO interface ( sort(a) -> a.sort() )
# so backward compatibility is not a good enough excuse.
# Oh, and not having some dup() method kinda sucks.
def fun_sort(lst):
    lst = [el for el in lst]
    lst.sort()
    return lst
