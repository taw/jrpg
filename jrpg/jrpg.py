#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, pygame, pickle
from math import sqrt, floor
from random import *
import time
import codecs # Python Unicode Brain Damage

# Import other jrpg modules
import images
from models.demons.book import Book_of_demons
from models.demons.chapterfactory import Chapter_factory

from models.worlds.town import *
from models.worlds.castle import *
from models.xpctl import XpCtl

import util
from mistakes import Mistakes
from util import sgn, Cached, Notifier, fun_sort
from terrain import corner_shader

# With regards to Unicode, Python isn't simply clueless.
# Clueless simply means a lack of clue. Unicode support in Python
# is much worse than that - it actually involves a lot of anticlue.
# The idea that the program shoud die with UnicodeEncodeError
# when it tries to write Unicode characters to a pipe or a file,
# but not to the console (whatever the locale may be)
# is the most braindead idea in computing since <marquee> tag.
# It purposedly break ability to talk with tools like less,
# head or Eclipse, and without any sane (= not involving any
# program modifications) workarounds..
#
# This workaround is for debugging only, we don't print anything
# interesting on the console during a normal run
#import codecs
#sys.stdin  = codecs.getwriter("utf-8")(sys.stdin)
#sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
#sys.stderr = codecs.getwriter("utf-8")(sys.stderr)


util.init_pygame("JRPG")

# Directory where all the images are, trailing / is needed
images_dir = "images/"

# Change this to False if you want jrpg to start in windowed mode
# Under Linux you can switch between windowed and fullscreen mode just by pressing Enter
# Under Windows it unfortunately does not work, and you need to select the mode here
# The default is to start in full screen mode.
full_screen_mode = True
# Bad things may happen if you set debug_mode = True
debug_mode       = False

# It may throw an exception on non-Unicode terminals, sorry
#savefile_verification = True # Always disable for public release
savefile_verification = False

if debug_mode:
    main_chara_speed =  8
else:
    main_chara_speed =  4
# xp_per_level(i) = 95i + 5i^2
# Last time I checked, it was 182 levels max

###########################################################
# A few helpful functions                                 #
###########################################################
def set_sym_diff(set1, set2):
    d = {}
    ds2 = []
    for i in set1:
        d[i] = 1
    for i in set2:
        if d.has_key(i):
            del d[i]      # In both sets
        else:
            ds2.append(i) # Only in the second set
    return (d.keys(), ds2)
def submatrix(mtx, x0, y0, xsz, ysz):
    return [[mtx[y][x] for x in range(x0,x0+xsz)] for y in range(y0,y0+ysz)]
def to_a(x):
    if x == None:
        return []
    elif type(x) == type([]):
        return x
    else:
        return [x]

#####################################################################
# Aux coords functions                                              #
#####################################################################
def W(y):
    return (0, y)
def E(y):
    return (9, y)
def N(x):
    return (x, 0)
def S(x):
    return (x, 9)
def We(y):
    return (-1, y)
def Ee(y):
    return (10, y)
def Ne(x):
    return (x, -1)
def Se(x):
    return (x, 10)

###########################################################
# This class manages the common and worldmap parts of UI  #
# It knows way too much about the world                   #
###########################################################

class UI:
    def __init__(self):
        mtctl_terrain = images.mtctl_terrain
        mtctl_enemies = images.mtctl_enemies
        mtctl_items   = images.mtctl_items
        ctdir         = images.ctdir

        # pygame.display.flip() has different behaviour under Windows and Mac
        self.running_under_windows = False
        self.running_under_mac = False
        self.running_fullscreen = True

        driver_name = pygame.display.get_driver()
        if driver_name == 'directx':
            self.running_under_windows = True
        elif driver_name == 'Quartz':
            self.running_under_mac = True

        global full_screen_mode
        self.clock    = pygame.time.Clock()
        size = (width, height) = 640, 480
        self.text     = []

        pygame.display.set_icon(pygame.image.load("images/jrpg-icon.png"))
        if full_screen_mode:
            if self.running_under_windows:
                self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
            elif self.running_under_mac:
                self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
            else:
                self.screen = pygame.display.set_mode(size, pygame.DOUBLEBUF|pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(size, pygame.DOUBLEBUF)
        self.font, self.font_med, self.font_big = util.load_font(18, 40, 64)

        self.key = [False for i in range(512)]
        self.mtctl = Map_Tiles_Controller(images_dir+"angband.png", mtctl_terrain, mtctl_enemies, mtctl_items)
        self.chara_tiles_dir = {}
        for k in ctdir:
            self.chara_tiles_dir[k] = pygame.image.load(images_dir+ctdir[k]).convert_alpha()

        self.nctl_msg_changed = Notifier()

        # FIXME: change the code to use these classes instead:
        self.map_viewport       = self.screen.subsurface(((0,0),(320,320)))
        self.stats_viewport     = self.screen.subsurface(((320, 0),(320, 160)))
        self.demonname_viewport = self.screen.subsurface(((320, 160),(320, 160)))
        self.msg_viewport       = self.screen.subsurface(((0,320),(640,160)))

        self.stats_cache      = Cached(lambda: mhc.render_statistics(self.stats_viewport), mhc.nctl_stats_changed)
        self.msg_cache        = Cached(lambda: self.msg_render(), self.nctl_msg_changed)
    def toggle_fullscreen(self):
        if self.running_fullscreen:
			self.screen = pygame.display.set_mode((0,0),pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)
			self.running_fullscreen = False
			self.stats_cache.invalidate()
			self.msg_cache.invalidate()
        else:
			self.screen = pygame.display.set_mode((0,0),pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.FULLSCREEN)
			self.running_fullscreen = True
			self.stats_cache.invalidate()
			self.msg_cache.invalidate()
    def msg_render(self):
        self.msg_viewport.fill((0,0,0))
        self.render_text_multicolor(self.msg_viewport, self.font, self.text, (32,32), (0,0), 24)
    def world_render(self): # API changes
        self.map_viewport.fill((0,0,0))
        wv.render()
        self.msg_cache.execute()
        self.stats_cache.execute()
        main_hero.render()
    def main_loop(self):
        # TODO: integrate with Battle_UI
        while True:
            self.world_main_loop_iter()

    def quick_help(self):
        help = [
            U"WORLD MODE",
            U"F1        - Quick help                                    ",
            U"F2        - Save game                                     ",
            U"F4        - Load game                                     ",
            U"TAB       - Take a closer look at the last demon          ",
            U"Arrows    - move around                                   ",
            U"Enter     - Toggle fullscreen                             ",
            U"Escape    - Exit game                                     ",
            U"BATTLE MODE",
            U"A-Z       - Type demon names                              ",
            U"Backspace - Erase text                                    ",
            U"Space     - Accept text                                   ",
            U"Press any key to continue",
        ]

        quick_help_viewport = self.screen.subsurface((0,0),(640,320))
        self.stats_cache.invalidate()
        quick_help_viewport.fill((0,0,128))

        self.render_text_unicolor(quick_help_viewport, ui.font, help, (320,0), (0.5, 0), (0,255,0), 24)

        quick_help_mode = True
        while quick_help_mode:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    quick_help_mode = False
                    self.key_down(event.key)
                    if event.key == pygame.K_RETURN:
                        self.toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE:
                        mhc.exit()
                    elif event.key == pygame.K_F1:
                        self.quick_help()
                    elif event.key == pygame.K_F2:
                        mhc.save()
                    elif event.key == pygame.K_F4:
                        mhc.load()
                        mhc.save()
                    elif event.key == pygame.K_TAB or event.key == pygame.K_F12:
                        mhc.closeup()
                elif event.type == pygame.KEYUP:
                    self.key_up(event.key)
            ui.tick()
        quick_help_viewport.fill((0,0,0))

    def world_main_loop_iter(self):
        # Check UI events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self.key_down(event.key)
                if event.key == pygame.K_RETURN:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    mhc.exit()
                elif event.key == pygame.K_F1:
                    self.quick_help()
                elif event.key == pygame.K_F2:
                    mhc.save()
                elif event.key == pygame.K_F4:
                    mhc.load()
                elif event.key == pygame.K_TAB or event.key == pygame.K_F12:
                    mhc.closeup()
                elif debug_mode and event.key == ord('e'): # debug
                    mhc.receive_money(1)
                elif debug_mode and event.key == ord('x'): # debug
                    mhc.get_xp(25)
                elif debug_mode and event.key == ord('c'): # debug
                    mhc.quest_do(cheat_quest[cheat_quest[0]])
                    self.change_text([U"Quest %s done by cheating" % cheat_quest[cheat_quest[0]]])
                    cheat_quest[0] = cheat_quest[0] + 1
                elif debug_mode and event.key == ord('n'): # debug
                    # Nuke all enemies on the map
                    for oid in range(len(wm.objects)):
                        if wm.objects[oid].__class__ == Map_object_enemy:
                            wm.objects[oid] = None
            elif event.type == pygame.KEYUP:
                self.key_up(event.key)
        # Controller
        speed_sn = 0
        speed_ew = 0
        # Dvorak a,oe or Qwerty awsd
        if ui.key_pressed(pygame.K_UP): # or ui.key_pressed(ord('.')):
            speed_sn = speed_sn - 1
        if ui.key_pressed(pygame.K_DOWN): # or ui.key_pressed(ord('e')):
            speed_sn = speed_sn + 1
        if ui.key_pressed(pygame.K_LEFT): # or ui.key_pressed(ord('o')):
            speed_ew = speed_ew - 1
        if ui.key_pressed(pygame.K_RIGHT): # or ui.key_pressed(ord('u')):
            speed_ew = speed_ew + 1
        main_hero.move(speed_ew*main_chara_speed, speed_sn*main_chara_speed)
        wm.run_charas()
        self.world_render()
        ui.tick()
    def tick(self):
        pygame.display.flip()
        #pygame.display.update()
        fpsLimit = 40
        if 1: # Low-CPU version
            time_so_far = self.clock.tick()
            time_max    = int(1000.0/fpsLimit)
            time_left   = time_max - time_so_far
            if time_left > 0:
                pygame.time.wait(time_left)
            #print time_left, self.clock.get_fps()
        else: # Version for exact measurement - do not use :-)
            self.clock.tick()
            print self.clock.get_fps()
    def key_down(self, key):
        self.key[key] = True
    def key_up(self, key):
        self.key[key] = False
    def key_pressed(self, key):
        return(self.key[key])
    def change_text(self, new_text, new_text_color=(0,255,0)):
        self.text = [(t, new_text_color) for t in new_text]
        self.nctl_msg_changed.fire()
    def append_text(self, new_text, new_text_color=(0,255,0)):
        if not new_text:
            return
        self.text = self.text + [(t, new_text_color) for t in new_text]
        # Save only the last 5 lines, if there are too many
        if len(self.text) > 5:
            self.text = self.text[len(self.text)-5:len(self.text)]
        self.nctl_msg_changed.fire()
    #####################################################################
    # Helper text-rendering function                                    #
    # anchor (0.0, 0.0) - loc is text's top left corner                 #
    # anchor (0.5, 0.5) - loc is text's center                          #
    # anchor (1.0, 1.0) - loc is text's bottom right corner             #
    # row_spacing - *total* distance between rows (not only whitespace) #
    #####################################################################
    def render_text_unicolor(self, target, font, text, loc, anchor, color, row_spacing=0):
        text = [(t,color) for t in text]
        self.render_text_multicolor(target, font, text, loc, anchor, row_spacing)
    def render_text_multicolor(self, target, font, text, loc, anchor, row_spacing):
        for i in range(len(text)):
            (t, color) = text[i]
            text_r = font.render(t, True, color)
            (x, y)   = loc
            (w, h)   = (text_r.get_width(), text_r.get_height())
            (ax, ay) = anchor
            fin_loc = (floor(x-ax*w),floor(y+i*row_spacing-ay*h))
            target.blit(text_r, fin_loc)
    def render_furi(self, target, furicode, (x,y), (size_limit,font_main,font_subst),
                    font_furi, color_base, color_furi, display_all_furi):
        # No space for too many characters
        if sum([len(base) for (base,furi,keep_furi) in furicode]) > size_limit:
            font_main = font_subst
        for i in range(len(furicode)):
            (base,furi,keep_furi) = furicode[i]
            base_r = font_main.render(base, True, color_base)
            target.blit(base_r, (x,y))
            (w,h) = (base_r.get_width(), base_r.get_height())
            if furi and (keep_furi or display_all_furi):
                if keep_furi:
                    furi_r = font_furi.render(furi, True, color_base)
                else:
                    furi_r = font_furi.render(furi, True, color_furi)
                (fw,fh) = (furi_r.get_width(), furi_r.get_height())
                target.blit(furi_r, (x-fw/2+w/2,y-fh))
            x = x + w
    # Others should be converted to target-taking form too
    def render_tile(self, target, target_rect, tile_id):
        if not tile_id: return
        source_rect = self.mtctl.ttt[tile_id][0]
        target.blit(self.mtctl.img, target_rect, source_rect)
    def render_enemy(self, target_surface, target_rect, enemy_id):
        target_surface.blit(self.mtctl.img, target_rect, self.mtctl.ett[enemy_id])
    def render_item(self, target_surface, target_rect, item_id):
        target_surface.blit(self.mtctl.img, target_rect, self.mtctl.itt[item_id])
    def chara_img(self, chara_class):
        return self.chara_tiles_dir[chara_class]
###########################################################
# This class manages map tiles characteristics            #
# (merge with UI)                                         #
###########################################################
class Map_Tiles_Controller:
    def __init__(self, img, ttt, ett, itt):
        self.ttt = {}
        for k in ttt:
            (sx, sy, bs) = ttt[k]
            self.ttt[k] = (pygame.Rect(sx*32, sy*32, 32, 32), bs)
        self.ett = {}
        for k in ett:
            (sx, sy) = ett[k]
            self.ett[k] = pygame.Rect(sx*32, sy*32, 32, 32)
        self.itt = {}
        for k in itt:
            (sx, sy) = itt[k]
            self.itt[k] = pygame.Rect(sx*32, sy*32, 32, 32)
        self.img = pygame.image.load(img).convert_alpha()

        # TODO: Find the coolest shape
        def alpha_test(x,y):
            return ((x+2)*(y+2) <= 30)

        self.corners = {}
        for tile in ttt:
            source_rect = self.ttt[tile][0]
            (x,y) = (source_rect.left, source_rect.top)
            p_ul = pygame.Surface((16,16)).convert_alpha()
            p_ul.blit(self.img, (0,0), (x,   y,   16,16))
            p_ur = pygame.Surface((16,16)).convert_alpha()
            p_ur.blit(self.img, (0,0), (x+16,y,   16,16))
            p_dl = pygame.Surface((16,16)).convert_alpha()
            p_dl.blit(self.img, (0,0), (x,   y+16,16,16))
            p_dr = pygame.Surface((16,16)).convert_alpha()
            p_dr.blit(self.img, (0,0), (x+16,y+16,16,16))
            # Apply alpha masks
            for x in range(16):
                for y in range(16):
                    (r,g,b,a) = p_ul.get_at((x,y))
                    if alpha_test(x,y):
                        a = 255
                    else:
                        a = 0
                    p_ul.set_at((x,y),(r,g,b,a))
                    (r,g,b,a) = p_ur.get_at((x,y))
                    if alpha_test(15-x,y):
                        a = 255
                    else:
                        a = 0
                    p_ur.set_at((x,y),(r,g,b,a))
                    (r,g,b,a) = p_dl.get_at((x,y))
                    if alpha_test(x,15-y):
                        a = 255
                    else:
                        a = 0
                    p_dl.set_at((x,y),(r,g,b,a))
                    (r,g,b,a) = p_dr.get_at((x,y))
                    if alpha_test(15-x,15-y):
                        a = 255
                    else:
                        a = 0
                    p_dr.set_at((x,y),(r,g,b,a))
            self.corners[tile] = [p_ul, p_ur, p_dl, p_dr]
    def blocking(self, tile_id):
        if not tile_id:
            return True
        return self.ttt[tile_id][1]

#############################################################
# This class is needed merely for the statistics            #
#############################################################
class Main_Hero_Controller:
    def __init__(self):
        self.hpmax  = 5
        self.hp     = self.hpmax
        self.xp     = 0
        self.level  = 0
        self.xpctl  = XpCtl()
        self.quests = {}
        self.money  = 0
        self.inventory = []
        # Protection against accidental F2(SAVE) when F4(LOAD) was actually meant
        self.save_warned = False
        # Protection against accidental F4(LOAD) when F2(SAVE) was actually meant
        self.make_load_warning = False
        # Protection against accidental ESC
        self.make_exit_warning = False

        self.nctl_stats_changed = Notifier()

        self.demon_closeup = None
        self.demon_closeup_kind = ""
    def set_closeup(self, soul, kind):
        self.demon_closeup = soul
        self.demon_closeup_kind = kind
    def closeup(self):
        if self.demon_closeup:
            body = self.demon_closeup
            msg = U"You see %s %s (%s)." % (self.demon_closeup_kind, body.short_dn(), " ".join(body.secret_names()))
            hints = body.get_hints()
            if not hints: hints = []
            ui.append_text([msg] + hints, (0,0,255))
        else:
            ui.append_text([U"No dead demon's body to look at"], (0,0,255))
    def gain_item(self, item):
        # (May duplicate), newest items first
        self.inventory = [item] + self.inventory
        self.nctl_stats_changed.fire()

        self.make_load_warning = True
        self.make_exit_warning = True
    def loss_item(self, item):
        # Loss every item of kind X
        self.inventory = [i for i in self.inventory if i != item]
        self.nctl_stats_changed.fire()

        self.make_load_warning = True
        self.make_exit_warning = True
    # One can only get XP for the same kind of demon 3 times
    def xp_for_kill(self, soul):
        if self.xpctl.maxed(soul.xp_code()):
            return
        if self.xpctl.seen_soul(soul):
            self.xpctl.beat(soul.xp_code())
            self.get_xp(soul.xp_for_win())
        else:
            self.make_load_warning = True
            self.make_exit_warning = True
            self.xpctl.see(soul.xp_code())
    def get_xp(self, xp_gained):
        self.make_load_warning = True
        self.make_exit_warning = True

        self.xp = self.xp + xp_gained
        new_level = self.level+1
        next_level_xp_req = new_level * (95 + new_level * 5)
        while self.xp >= next_level_xp_req :
            self.level = self.level + 1
            self.hpmax = self.hpmax + 1
            self.hp    = self.hp + 1
            new_level  = self.level+1
            next_level_xp_req = new_level * (95 + new_level * 5)
        self.nctl_stats_changed.fire()
    def change_hp(self, new_hp):
        self.hp = new_hp
        self.nctl_stats_changed.fire()

        self.make_load_warning = True
        self.make_exit_warning = True
    # For battle damage
    def hit(self, damage):
        self.make_load_warning = True
        self.make_exit_warning = True

        self.hp = self.hp - damage
        if self.hp < 0:
            self.hp = 0
        # if self.hp == 0:
        #     we're dead, but it's up to the caller to take care of
        self.nctl_stats_changed.fire()
    # For worldmap damage
    def damage(self, damage):
        self.make_load_warning = True
        self.make_exit_warning = True

        self.hit(damage)
        if self.hp == 0:
            wm.teleport_to_hospital()
        self.nctl_stats_changed.fire()
    # This code works in battle mode and in worldmap mode
    def render_statistics(self, target):
        target.fill((0,0,0))
        ui.render_text_unicolor(target, ui.font, [
                      "Level: %d" % self.level,
                      "XP:    %d" % self.xp,
                      "HP:    %d/%d" % (self.hp, self.hpmax),
                      "Money: %d coins" % self.money,
                      ],
                      (32, 32), (0,0), (0, 255, 0), 24)
        for i in range(len(self.inventory)):
            ui.render_item(target, (32+i*32,32+24*4), self.inventory[i])
    def quest_is_done(self, quest_id):
        return self.quests.has_key(quest_id)
    def quest_do(self, quest_id):
        self.make_load_warning = True
        self.make_exit_warning = True
        self.quests[quest_id] = True
    def has_money(self, amount):
        return self.money >= amount
    # We're assuming that self.has_money(amount) is true
    def take_money(self, amount):
        self.make_load_warning = True
        self.make_exit_warning = True
        self.money = self.money - amount
        self.nctl_stats_changed.fire()
    def receive_money(self, amount):
        self.make_load_warning = True
        self.make_exit_warning = True
        self.money = self.money + amount
        self.nctl_stats_changed.fire()
    def save(self):
        # Verify that the xp in the savefile is not higher than your XP
        xp = 0
        try:
            f = open("savefile", "r")
            ld = pickle.load(f)
            xp = ld["xp"]
        except IOError, (errno, strerror):
            pass
        if xp > self.xp and not self.save_warned:
            ui.change_text([U"Warning: In the save file you have higher experience (%d)" % xp,
                            U"than in the game (%d)." % self.xp,
                            U"If you want to save anyway, press F2 again"], (255,0,0))
            self.save_warned = True
            return
        f = open("savefile", "w")
        save_data = {
            "name"     : "Freya",
            "hpmax"    : self.hpmax,
            "hp"       : self.hp,
            "xp"       : self.xp,
            "level"    : self.level,
            "xpfor"    : self.xpctl.dump(),
            "money"    : self.money,
            "quests"   : self.quests,
            "inventory": self.inventory,
        }
        pickle.dump(save_data, f)
        f.close()
        self.save_warned = False
        if xp > self.xp:
            ui.change_text([U"Game with reduced XP saved on your explicit request"])
        else:
            ui.change_text([U"Game saved"])
        self.make_exit_warning = False
        self.make_load_warning = False
    def load(self):
        if self.make_load_warning:
            ui.change_text([U"Something happened since the last saving",
                            U"Do you really want to load ?",
                            U"Press F4 again to load."])
            self.make_load_warning = False
            return
        try:
            f = open("savefile", "r")
            ld = pickle.load(f)
            self.hpmax     = ld["hpmax"]
            self.hp        = ld["hp"]
            self.xp        = ld["xp"]
            self.level     = ld["level"]
            self.xpctl     = XpCtl(ld["xpfor"])
            self.quests    = ld["quests"]
            self.money     = ld["money"]
            # Just a backward compatibility hack
            # remove after the next savefile format change
            #self.inventory = ld["inventory"]
            self.inventory = ld.get("inventory", [])

            # It may crash on non-Unicode terminals
            if savefile_verification:
                self.verify_xp()
            self.nctl_stats_changed.fire()
            # Teleport to the hospital ;-)
            # Save/load is a very traumatic experience
            wm.teleport_to_hospital()
            self.make_exit_warning = False
            self.make_load_warning = False
            self.last_demon_killed = None
        except IOError, (errno, strerror):
            ui.change_text([U"Can't load the savefile: ", unicode(strerror)], (255,0,0))
    def exit(self):
        if self.make_exit_warning:
            ui.change_text([U"Something happened since the last saving",
                            U"Do you really want to exit ?",
                            U"Press ESCAPE again to exit."])
            self.make_exit_warning = False
        else:
            sys.exit()
    # This is some dead code, do not run
    def verify_xp(self):
        global w
        demons = book.demons
        demon_ok = {}
        for demon_class in demons.keys():
            for demon in demons[demon_class]:
                demon_ok[demon.xp_code()] = True
        free_xp = 0
        for defeated_demon_xp_code in self.xpctl.xpfor.keys():
            if demon_ok.has_key(defeated_demon_xp_code):
                pass
                # print "Good demon %s (%d)" % (defeated_demon_xp_code, self.xpfor[defeated_demon_xp_code])
            else:
                print "Bad demon %s (%d)" % (defeated_demon_xp_code, self.xpctl.xpfor[defeated_demon_xp_code])
                free_xp = free_xp + self.xpctl.xpfor[defeated_demon_xp_code]
        if free_xp != 0:
            print "Free XP: ", free_xp
        self.print_xp_statisticts()
        self.print_kanji_knowledge()
    def print_xp_statisticts(self):
        demons = book.demons
        max_xp = 0
        max_level = 0
        for chapter in demons:
            for demon in demons[chapter]:
                max_xp += 3 * demon.xp_for_win()

        while max_xp >= (max_level+1) * (95 + (max_level+1) * 5):
            max_level += 1
        print u"Max possible XP:    ", max_xp
        print u"Max possible level: ", max_level

        # Hiragana
        stat = [0, 0, 0, 0, 0]
        for demon in demons[0]:
            stat[self.xpctl.xpfor.get(demon.xp_code(), -1) + 1] += 1
        print u"Hiragana:"
        print u"* not met  ", stat[0]
        print u"* 0 xp     ", stat[1]
        print u"* 1 xp     ", stat[2]
        print u"* 2 xp     ", stat[3]
        print u"* 3 xp     ", stat[4]
        # Katakana
        stat = [0, 0, 0, 0, 0]
        for demon in demons[1]:
            stat[self.xpctl.xpfor.get(demon.xp_code(), -1) + 1] += 1
        print u"Katakana:"
        print u"* not met  ", stat[0]
        print u"* 0 xp     ", stat[1]
        print u"* 1 xp     ", stat[2]
        print u"* 2 xp     ", stat[3]
        print u"* 3 xp     ", stat[4]
        # Kana word
        stat = [0, 0, 0, 0, 0]
        for demon in demons[2]:
            stat[self.xpctl.xpfor.get(demon.xp_code(), -1) + 1] += 1
        print u"Kana word:"
        print u"* not met  ", stat[0]
        print u"* 0 xp     ", stat[1]
        print u"* 1 xp     ", stat[2]
        print u"* 2 xp     ", stat[3]
        print u"* 3 xp     ", stat[4]
        # Kanji demons2
        stat = [0, 0, 0, 0, 0, 0]
        for demon in demons[3]:
            xp = self.xpctl.xpfor.get(demon.xp_code(), -1)
            if xp == 3 and self.xpctl.xpfor.get(demons[3][demon.subsumed_by()].xp_code(), 0) >= 1:
                xp = 4
            stat[xp + 1] += 1
        print u"Kanji demons (JLPT 4+3+2):"
        print u"* not met  ", stat[0]
        print u"* 0 xp     ", stat[1]
        print u"* 1 xp     ", stat[2]
        print u"* 2 xp     ", stat[3]
        print u"* 3 xp     ", stat[4]
        print u"* subsumed ", stat[5]
    def print_kanji_knowledge(self):
        kanji_knowledge = self.get_kanji_knowledge()
        print u"Kanji known:"
        print u"Not at all: ", kanji_knowledge[0]
        print u"Just a bit: ", kanji_knowledge[1]
        print u"Quite well: ", kanji_knowledge[2]
        print u"Very well:  ", kanji_knowledge[3]
        print u"Perfectly:  ", kanji_knowledge[4]
    def get_kanji_knowledge(self):
        # The idea is that every demon contains some kanjis
        # Let's fill the kanji table ...
        # kanji_stats[日] = [demons_never_met, demons_not_beaten, demons_beaten_1x, demons_beaten_2x, demons_beaten_3x]
        # etc.
        # Then we can print statistics of some sort ... ^_^
        demons = book.demons
        kanji_stats = {}

        # To make the result a bit more relevant and
        # the crystal ball feel a bit less mean use the following mapping:
        # None, 0 -> 0
        # 1       -> 2
        # 2,3     -> 3
        for demon in demons['kanji']:
            xp = self.xpctl.xpfor.get(demon.xp_code(), 0)
            if xp == 1 or xp == 2: xp += 1
            for kanji in demon.kanji():
                if not kanji_stats.has_key(kanji):
                    kanji_stats[kanji] = [0, 0]
                kanji_stats[kanji][0] += xp
                kanji_stats[kanji][1] += 3
        #kanji_stats2 = {}
        # 0%, 1..24%, 25%..49%, 50%..99%, 100%
        kanji_stats_final = [0, 0, 0, 0, 0]
        # Now invert the stats
        for k in kanji_stats.keys():
            # list objects are not hashable
            a,b = kanji_stats[k]
            if a==0: kanji_stats_final[0] += 1 # 0%
            elif a==b: kanji_stats_final[4] += 1 # 100%
            elif a*4/b==0: kanji_stats_final[1] += 1 # 1%..24%
            elif a*4/b==1: kanji_stats_final[2] += 1 # 25%..49%
            else: kanji_stats_final[3] += 1 # 50%..99%

            #if not kanji_stats2.has_key(v):
            #    kanji_stats2[v] = []
            #kanji_stats2[v].append(k)

        #for k in fun_sort(kanji_stats2.keys()):
        #    print k, u"% - ", u"".join(kanji_stats2[k])
        return kanji_stats_final
###########################################################
# This class controls a single map object                 #
###########################################################
# FIXME: convert to something sanely-OO
# FIXME: There should be priorities for both render and event
class Map_object: # virtual class
    def event(self):
        self.f_event()
    def attach_event(self, event):
        self.f_event = event
    #def get_bb(self):
    #    return self.val_bbox
    #def render(self):
    #    self.f_render()

class Map_object_enemy(Map_object):
    def __init__(self, (x, y), enemy_sprite, event=None):
        self.x = x
        self.y = y
        self.enemy_sprite = enemy_sprite
        self.f_event   = event
    def render(self):
        ui.render_enemy(ui.map_viewport, (32*self.x-wv.shift_x, 32*self.y-wv.shift_y), self.enemy_sprite)
    def get_bb(self):
        return pygame.Rect((self.x*32 ,self.y*32), (32, 32))

class Map_object_item(Map_object):
    def __init__(self, (x, y), item_class, event=None):
        self.x = x
        self.y = y
        self.item_class = item_class
        self.f_event   = event
    def render(self):
        ui.render_item(ui.map_viewport, (32*self.x-wv.shift_x, 32*self.y-wv.shift_y), self.item_class)
    def get_bb(self):
        return pygame.Rect((self.x*32, self.y*32), (32, 32))

############################################################
# This class controls a single character's movement        #
# No high-level information like equipment etc. should be  #
# put here, it should be merely for the display            #
# and moving around.                                       #
############################################################
class Chara:
    Sprite_up    = 0
    Sprite_right = 1
    Sprite_down  = 2
    Sprite_left  = 3
    def __init__(self, chara_class, position=None, route=None):
        self.img     = ui.chara_img(chara_class)
        self.dt      = Chara.Sprite_down
        self.step    = 0
        self.spp     = 0
        self.is_main = False
        if position and route:
            raise "Trying to set chara position both as position and as route"
        if not position and not route:
            raise "Chara position not seit as either position or route"
        # Do something about positions and paths
        if position:
            (x,y)        = position
            self.pos     = (32*x, 32*y)
            self.route   = None
            self.route_i = 0
        else:
            self.route   = route
            # Just for testing
            self.route_i = 0
            (x,y)        = self.route[0]
            self.pos     = (32*x, 32*y)
            tr           = self.trace()
            # Random point of the route
            self.pos,self.route_i = choice(tr)
#    def setup_route(self, route):
#       self.route   = route
#       self.route_i = 0
#
#        print "Route trace:"
#        for ((x,y),i) in self.trace():
#            print "(%d,%d) -> (%d,%d)[%d]" % (x,y,self.route[i][0],self.route[i][1],i)
    # This is a high-level command
    def patrol(self,speed=1):
        if self.goto(self.route[self.route_i], speed):
            self.route_i = (self.route_i + 1) % len(self.route)
    # This is a high-level command
    # return True if the destination is reached, or can't move in that direction
    # Include destination in the trace, otherwise only half of a trace like
    # this one will be included:(X,2,3,X)
    #
    # 1   3
    # .\ /|
    # . X |
    # .. \|
    # 4   2
    def trace(self):
        tr  = {}
        tr2 = []
        i   = 0
        while tr.get((self.pos,self.route_i)) == None:
            tr[(self.pos,self.route_i)] = i
            tr2.append((self.pos,self.route_i))
            i = i+1
            self.patrol(1)
        # return a trace from the first intersection point
        return tr2[tr[(self.pos,self.route_i)]:len(tr2)]
    # return True if already there or cannot move
    def goto(self, (tx, ty), speed=1):
        dx = sgn(tx * 32 - self.pos[0])
        dy = sgn(ty * 32 - self.pos[1])
        if dx == 0 and dy == 0:
            return True
        else:
            return not self.move(dx*speed, dy*speed)
    def move_blocked(self, new_pos):
        if wm.collides(pygame.Rect(new_pos[0], new_pos[1], 24, 24)):
            return True
    def teleport(self, new_pos):
        self.pos   = new_pos
        # Keep self.dt
        self.step  = 0
        self.spp   = 0
    # Very low-level interface
    # Just move and trigger event handlers
    # Do not change sprite direction
    # if we move to a blocked position it's an error !
    def real_move(self, new_pos):
        # First move, then call event handlers, because they may teleport the chara
        old_pos = self.pos
        self.pos = new_pos
        if self.is_main:
        # Should be triggered even when standing (chara-bound events, maybe enemy-bound too)
            wm.move_events(old_pos, new_pos)
            wv.center_at(self.pos)
            wv.surface_cache_valid = False
    # Low level interface
    # return False if can't move at all (even only along one axis)
    def move(self, dx, dy):
        if dx == 0 and dy == 0:
            return True
        (cx,cy) = self.pos
        # If big move is blocked, try moving small a few times
        if self.move_blocked((cx+dx, cy+dy)) and (abs(dx)>1 or abs(dy)>1):
            # Assumes that dx * sgn(dx) == dy * sgn(dy)
            # (= move is either straight or diagonal)
            mx = max(abs(dx), abs(dy))
            dxs = sgn(dx)
            dys = sgn(dy)
            for i in range(mx):
                self.move(dxs,dys)
            return True
        if dx == 0 or dy == 0:
            self.set_direction(dx, dy)
            # If straight is blocked, try 90-off to the nearest unblocked
            # (not further away than 32px)
            new_pos = (cx+dx, cy+dy)
            if self.move_blocked(new_pos):
                # blocked implies |dx|<=1 && |dy|<=1
                #print "Trying to move %d %d" % (dx, dy)
                res_a = 32 # 32 - too far
                res_b = 32 # 32 - too far
                #print "Trying to move %d %d" % (dxs, dys)
                for i in range(1,res_a): # 1..31
                    if self.move_blocked((cx+dy*i, cy-dx*i)):
                        break
                    if not self.move_blocked((cx+dy*i+dx, cy-dx*i+dy)):
                        res_a = i
                        break
                for i in range(1,res_b): # 1..31
                    if self.move_blocked((cx-dy*i,cy+dx*i)):
                        break
                    if not self.move_blocked((cx-dy*i+dx, cy+dx*i+dy)):
                        res_b = i
                        break
                #print "Res %d %d" % (res_a, res_b)
                # Trying to push against a wall or with sideways blocked
                if res_a == 32 and res_b == 32:
                    return False
                if res_a <= res_b:
                    new_pos = (cx+dy, cy-dx)
                else:
                    new_pos = (cx-dy, cy+dx)
            self.real_move(new_pos)
            return True
        # Diagonal movement
        else:
            # If diagonal is blocked, maybe some 45-off straight
            # movement is possible
            candidates = [
                (dx,dy,(cx+dx, cy+dy)),
                (dx, 0,(cx+dx, cy+ 0)),
                ( 0,dy,(cx+ 0, cy+dy)),
            ]
            for (adx,ady,new_pos) in candidates:
                # It's an error if adx == 0 and ady == 0
                if (adx != 0 or ady != 0) and not self.move_blocked(new_pos):
                    self.set_direction(adx, ady)
                    self.real_move(new_pos)
                    return True
        return False
    def set_direction(self, dx, dy):
        if dx > 0:
            dx = 1
        elif dx < 0:
            dx = -1
        if dy > 0:
            dy = 1
        elif dy < 0:
            dy = -1
        d = 3 * dy + dx
        # We have 9 movement directions, but only 4 sprite directions
        if d == -4: # Left/Up
            if self.dt != Chara.Sprite_up:
                self.dt = Chara.Sprite_left
        elif d == -3: # Up
            self.dt = Chara.Sprite_up
        elif d == -2: # Right/Up
            if self.dt != Chara.Sprite_up:
                self.dt = Chara.Sprite_right
        elif d == -1: # Left
            self.dt = Chara.Sprite_left
        elif d == 0: # Standing still
            pass
        elif d == 1:
            self.dt = Chara.Sprite_right
        elif d == 2: # Left/Down
            if self.dt != Chara.Sprite_down:
                self.dt = Chara.Sprite_left
        elif d == 3: # Down
            self.dt = Chara.Sprite_down
        else: # d = 4 # Right/Down
            if self.dt != Chara.Sprite_down:
                self.dt = Chara.Sprite_right
        if d == 0:
            self.step = 1
        else:
            self.spp = self.spp + 1
            if self.spp == 5:
                self.spp = 0
                self.step = (self.step + 1) % 4
    def render(self):
        # Chara location on the ground is 24x24 square
        # 8 bits above it should simply be ignored
        if self.step == 3:
            s = 1
        else:
            s = self.step
        ui.map_viewport.blit(self.img, (self.pos[0]-wv.shift_x,self.pos[1]-8-wv.shift_y), pygame.Rect(24 * s, 32 * self.dt, 24, 32))

###########################################################
class End_of_battle(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return `self.value`

###########################################################
class Enemy_in_battle:
    def __init__(self, (x,y), demon, sprite_class, demon_class, (active_color,inactive_color), power):
        self.x              = x
        self.y              = y
        self.dx             = 0
        self.dy             = 0
        self.demon          = demon
        self.active         = False
        self.sprite_class   = sprite_class
        self.hit_chara      = False
        self.fresh          = False # It's battle-round-freshness, not battle-freshness ;-)
        self.active_color   = active_color
        self.inactive_color = inactive_color
        self.power          = power
    def render(self):
        (x0,y0) = (self.x+self.dx, self.y+self.dy)
        ui.render_enemy(ui.map_viewport, (x0,y0), self.sprite_class)
        if self.active:
            text_color = self.active_color
        else:
            text_color = self.inactive_color
        ui.render_text_unicolor(ui.map_viewport, ui.font, [self.demon.short_dn()], (x0+16,y0), (0.5, 1.0), text_color)
    def render_name(self, target):
        color_kanji = (128, 255, 128)
        color_hint  = (255, 128, 255)
        ui.render_furi(target,self.demon.furicode(),(32,64),(4,ui.font_big,ui.font_med),
                       ui.font,color_kanji,color_hint,self.fresh)
        #print ("DEBUG sub sns ?: %s %s" % (self.demon.sub_sns(), self.fresh))
        if self.demon.sub_sns() and self.fresh:
            ui.render_text_unicolor(target, ui.font,
                [U"  ".join(self.demon.get_good_response())],(32,128), (0.0, 0.0), color_hint
            )
    def move(self):
        self.dx = self.dx + normalvariate(0,1)
        self.dy = self.dy + normalvariate(0,1)
        l = sqrt(self.dx*self.dx + self.dy*self.dy)
        if l > 32:
            self.dx = self.dx / l
            self.dy = self.dy / l
    def activate(self):
        self.active = True
    def deactivate(self):
        self.active = False
    def secret_name_ok(self, secret_name_guess):
        return self.demon.answer_ok(secret_name_guess)
    def get_hints(self):
        return self.demon.get_hints()

# This class should manage killing enemies and activation/deactivation etc.
class Battle_model:
    def __init__(self, active_look, inactive_look, sprite_class, demon_class, power):
        self.enemies   = []
        self.active    = -1

        self.nctl_demonname_changed = Notifier()

        enemies = book.choice(mhc.xpctl, 5, demon_class)
        locs = [
            (80, 80),
            (160, 70),
            (240, 60),
            (70, 160),
            (60, 240),
        ]
        for ((x,y),d) in zip(locs, enemies):
            enemy = Enemy_in_battle((x, y), d, sprite_class, demon_class, (active_look, inactive_look), power)
            self.enemies.append(enemy)
            enemy.fresh = not mhc.xpctl.seen_soul(enemy.demon)
        self.switch_active()

    def attacked(self, attack_name):
        if self.active == -1: # No active enemies
            pass
        if self.enemies[self.active].secret_name_ok(attack_name):
            if not self.enemies[self.active].hit_chara:
                mhc.xp_for_kill(self.enemies[self.active].demon)
            mhc.set_closeup(self.enemies[self.active].demon, "dead demon")
            self.kill_active(self.enemies[self.active])
        else:
            mistakes.mistake(attack_name, self.enemies[self.active].demon)
            mhc.set_closeup(self.enemies[self.active].demon, "angry demon")
            self.enemies[self.active].hit_chara = True
            self.enemies[self.active].fresh = False
            self.counter_attack(self.enemies[self.active], self.enemies[self.active].power)
            self.switch_active()
    def switch_active(self):
        if self.active != -1:
            self.enemies[self.active].deactivate()
        if len(self.enemies) > 0:
            self.active = randint(0, len(self.enemies)-1)
            self.enemies[self.active].activate()
        else:
            self.active = -1
        self.nctl_demonname_changed.fire()
    def kill_active(self, victim):
        ui.change_text([
            victim.demon.get_success_message()
        ])

        if self.active == -1:
            return
        self.enemies[self.active].deactivate()
        del self.enemies[self.active]
        self.active = -1
        if len(self.enemies) == 0:
            raise End_of_battle(True) # battle won
        self.switch_active()
    def counter_attack(self, attacker, damage):
        ui.change_text([attacker.demon.get_fail_message(damage)], (255,0,0))
        if not attacker.fresh:
            ui.append_text(attacker.get_hints(), (0,255,0))
        self.chara_hit(damage)
    def get_active_enemy(self):
        if self.active == -1:
            return None
        else:
            return self.enemies[self.active]
    def render(self):
        for e in self.enemies:
            e.render()
    def move(self):
        for e in self.enemies:
            e.move()
    def chara_hit(self,damage):
        mhc.hit(damage)
        if mhc.hp == 0:
            raise End_of_battle(False) # Battle lost

class Battle_UI:
    # Move the image load to some manager
    def __init__(self, look, sprite_class, demon_class, power):
        (bg_fn, self.active, inactive) = choice(images.battle_look_table[look])

        self.battle_bg = pygame.image.load(bg_fn).convert_alpha()

        self.chara_img = ui.chara_img("female-blue")
        self.chara_buf = U""

        ui.change_text([])
        self.bs_repeat = 0

        self.battle_model = Battle_model(self.active, inactive, sprite_class, demon_class, power)
        self.demonname_cache = Cached(lambda: self.demonname_render(), self.battle_model.nctl_demonname_changed)
    def demonname_render(self):
        ui.demonname_viewport.fill((0,0,0))
        active_enemy = self.battle_model.get_active_enemy()
        if active_enemy:
            active_enemy.render_name(ui.demonname_viewport)
            if active_enemy.fresh:
                ui.append_text(active_enemy.get_hints(), (0,0,255))
    def render(self):
        ui.map_viewport.blit(self.battle_bg, (0,0))
        self.battle_model.render()
        # (self.chara_x, self.chara_y) == (240, 240), always
        ui.map_viewport.blit(self.chara_img, (240, 240), (2*24, 3*32, 24, 32))
        # font_med can get out of the box
        ui.render_text_unicolor(ui.map_viewport, ui.font, [self.chara_buf],
                                (240+12, 240), (0.5, 1.0), self.active)
        self.demonname_cache.execute()
        ui.msg_cache.execute()
        ui.stats_cache.execute()
    def chara_attack(self,enemies):
        if self.chara_buf == U"":
            return
        enemies.attacked(self.chara_buf)
        self.chara_buf = U""
    # It's quite silly ...
    def main_loop(self):
        try:
            while True:
                self.battle_mode_loop_iter()
        except End_of_battle, (result):
            ui.demonname_viewport.fill((0,0,0))
            return result.value
    def battle_mode_loop_iter(self):
        # Check UI events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                ui.key_down(event.key)
                # If any key was pressed, stop backspacing
                # <backspace pressed> <a pressed> <backspace released> <a released>
                #                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                # The user probably meant to release backspace first and press a,
                # but without this hack a would get backspaced too
                if ui.key[pygame.K_BACKSPACE] and event.key != pygame.K_BACKSPACE:
                    ui.key_up(pygame.K_BACKSPACE)
                if event.key == pygame.K_RETURN:
                    ui.toggle_fullscreen()
                elif event.key == pygame.K_ESCAPE:
                    if mhc.make_exit_warning:
                        ui.change_text([U"Something happened since the last saving",
                                        U"Do you really want to exit ?",
                                        U"Press ESCAPE again to exit."])
                        mhc.make_exit_warning = False
                    else:
                        sys.exit()
                elif event.key == pygame.K_TAB or event.key == pygame.K_F12:
                    mhc.closeup()
                elif event.unicode >= 'a' and event.unicode <= 'z':
                    self.chara_buf = self.chara_buf + event.unicode
                elif event.unicode == ' ':
                    self.chara_attack(self.battle_model)
                elif event.key == pygame.K_BACKSPACE:
                    self.bs_repeat = -1
            elif event.type == pygame.KEYUP:
                ui.key_up(event.key)
        if ui.key[pygame.K_BACKSPACE]:
            if self.bs_repeat == -1: # Fresh
                self.chara_buf = self.chara_buf[0:len(self.chara_buf)-1]
                self.bs_repeat = 8
            if self.bs_repeat == 0:
                self.chara_buf = self.chara_buf[0:len(self.chara_buf)-1]
                self.bs_repeat = 2
            else:
                self.bs_repeat = self.bs_repeat - 1
        self.battle_model.move()
        self.render()
        ui.tick()

###########################################################
# The new world class                                     #
# Don't use without initial switch_map()                  #
###########################################################
class World_model:
    def __init__(self):
        self.map_db = {}
        self.map_db["world"] = {
            "tiles": self.load_map("maps/world.map"),
            "setup": lambda: self.map_setup_world(),
        }
        self.map_db["icy mountains"] = {
            "tiles": self.load_map("maps/icy_mountains.map"),
            "setup": lambda: self.map_setup_icy_mountains(),
        }
        self.map_db["hospital"] = {
            "tiles": self.load_map("maps/hospital.map"),
            "setup": lambda: World_hospital(self, ui, mhc)
        }

        self.map_db["library"] = {
            "tiles": self.load_map("maps/library.map"),
            "setup": lambda: World_library(self, ui, mhc)
        }

        self.map_db["wizard shop"] = {
            "tiles": self.load_map("maps/wizard_shop.map"),
            "setup": lambda: World_wizard_shop(self, ui, mhc),
        }
        self.map_db["angel sanctuary"] = {
            "tiles": self.load_map("maps/angel_sanctuary.map"),
            "setup": lambda: World_angel_sanctury(self, ui, mhc),
        }
        self.map_db["blacksmith"] = {
            "tiles": self.load_map("maps/blacksmith.map"),
            "setup": lambda: World_blacksmith(self, ui, mhc),
        }
        self.map_db["cave"] = {
            "tiles": self.load_map("maps/cave.map"),
            "setup": lambda: World_cave(self, ui, mhc),
        }
        self.map_db["castle"] = {
            "tiles": self.load_map("maps/castle.map"),
            "setup": lambda: World_castle(self, ui, mhc),
        }
        self.map_db["tower level 1"] = {
            "tiles": self.load_map("maps/tower_level_1.map"),
            "setup": lambda: World_tower_level1(self, ui, mhc),
        }
        self.map_db["tower level 2"] = {
            "tiles": self.load_map("maps/tower_level_2.map"),
            "setup": lambda: World_tower_level2(self, ui, mhc),
        }
        self.map_db["tower level 3"] = {
            "tiles": self.load_map("maps/tower_level_3.map"),
            "setup": lambda: World_tower_level3(self, ui, mhc),
        }
        self.map_db["dungeon level 1"] = {
            "tiles": self.load_map("maps/dungeon_level_1.map"),
            "setup": lambda: World_dungeon_level1(self, ui, mhc),
        }
        self.map_db["dungeon level 2"] = {
            "tiles": self.load_map("maps/dungeon_level_2.map"),
            "setup": lambda: World_dungeon_level2(self, ui, mhc),
        }
        self.map_db["dungeon level 3"] = {
            "tiles": self.load_map("maps/dungeon_level_3.map"),
            "setup": lambda: World_dungeon_level3(self, ui, mhc),
        }
        self.current_map = None
        self.current_map_id = None

    def switch_map(self, map_id, (x, y)):
        self.current_map_id = map_id
        # Copy, so we can change the tiles without modifying the database
        if not self.map_db[self.current_map_id]:
            raise Exception("No such map %s" % self.current_map_id)
        self.current_map = [[tile for tile in line] for line in self.map_db[self.current_map_id]["tiles"]]

        self.charas       = []
        self.chara_events = {}
        self.objects      = []
        self.enter_events = {}

        main_hero.teleport((x*32, y*32))

        self.map_db[self.current_map_id]["setup"]()

        wv.switch_map_event((x, y))

    def load_map(self, file_name):
        f = open(file_name)
        tiles = [line.rstrip('\n') for line in f.readlines()]
        f.close()
        return tiles

    def run_charas(self):
        for chara in self.charas:
            chara.patrol()

    def teleport_to_hospital(self):
        self.switch_map("hospital",(3,8))

    def collides(self, rect):
        # Convert rect from pixelspace to tilespace
        top    = rect.top    >> 5
        left   = rect.left   >> 5
        bottom = rect.bottom >> 5
        right  = rect.right  >> 5
        for i in range(top, bottom+1):
            for j in range(left, right+1):
                if ui.mtctl.blocking(self.current_map_get_element(j,i)):
                    return True
        return False

    # This map has no outside borders
    def current_map_get_element(self,x,y):
        if y<0 or y >= len(self.current_map) or x < 0 or x >= len(self.current_map[y]):
            return None
        return self.current_map[y][x]

    # self is not really used
    def pixel_rect_to_tile_rect(self, pixel_rect):
        top    = pixel_rect.top >> 5
        left   = pixel_rect.left >> 5
        bottom = pixel_rect.bottom >> 5
        right  = pixel_rect.right >> 5
        return pygame.Rect(left,top,right-left+1,bottom-top+1)

    def enter_event(self, tile):
        if self.enter_events.has_key(tile):
            for e in self.enter_events[tile]:
                e()
                return True
        return False
    def move_events(self, old_pos, new_pos):
        otr = self.pixel_rect_to_tile_rect(pygame.Rect(old_pos,(24,24)))
        old_tiles = [(otr.left+x,otr.top+y) for x in range(otr.width) for y in range(otr.height)]
        ntr = self.pixel_rect_to_tile_rect(pygame.Rect(new_pos,(24,24)))
        new_tiles = [(ntr.left+x,ntr.top+y) for x in range(ntr.width) for y in range(ntr.height)]
        (leaved,entered) = set_sym_diff(old_tiles,new_tiles)
        # If event returns True, don't run any more events
        # (it means the map changes or sth like that)
        # I'm not sure what are leave events doing
        for tile in entered:
            if self.enter_event(tile):
                return
        for chara in self.chara_events.keys():
            if self.collides_with_chara(new_pos, chara):
                event = self.chara_events[chara]
                event()
                return
        for o in self.objects:
            if o != None and o.f_event != None:
                if pygame.Rect(new_pos,(24,24)).colliderect(o.get_bb()):
                    o.event()
                    return
    def collides_with_chara(self, pos, chara):
        return pygame.Rect(pos,(24,24)).colliderect(pygame.Rect(chara.pos,(24,24)))
    # Setup all NPCs, events, items, enemies etc. for map world
    def wormhole(self, start_tile, new_map, end_tile):
        self.add_enter_event(start_tile, lambda: self.switch_map(new_map, end_tile))
    # This sucks - I can't decide whether there may be
    # only a single event, or more events are possible
    # Let's say that for now all events are "map changing events",
    # and they block other old-map's events from happening
    def add_chara_event(self, chara, event):
        self.chara_events[chara] = event
    def add_chara(self, chara_class, position = None, route = None, event = None):
        chara_obj = Chara(chara_class, position=position, route=route)
        self.charas.append(chara_obj)
        if event != None:
            self.add_chara_event(chara_obj, event)
    # FIXME: current map's tileset should not be shared with the map database
    # REFACTORME: limit prerender damage to (x-1..x+1) * (y-1..y+1)
    def change_tile(self, (x,y), new_tile):
        self.current_map[y][x] = new_tile
        wv.surface_cache_valid = False
        wv.prerender_cache_valid = False
    # These are for the main chara only
    def add_enter_event(self, tile, event):
        if not self.enter_events.has_key(tile):
            self.enter_events[tile] = []
        self.enter_events[tile].append(event)
    def add_enemy(self, enemy_loc, battle_look, sprite_class, demon_class, power):
        enemy_id = self.add_object(Map_object_enemy(enemy_loc, sprite_class))
        def fight():
            battle = Battle_UI(battle_look, sprite_class, demon_class, power)
            if battle.main_loop():
                # win - remove the sprite and the associated event
                self.remove_enemy(enemy_id)
            else:
                # loss
                self.switch_map("hospital",(3,8))
        self.add_enemy_event(enemy_id, fight)
    def add_item(self, loc, item_type, event=None):
        item_id = self.add_object(Map_object_item(loc, item_type))
        def grab():
            self.remove_item(item_id)
            event()
        # ones without any event need special handling
        # If an item is grabbable, but shouldn't do anything on-grab,
        # use an empty event lambda: ()
        if event:
            self.add_item_event(item_id, lambda: grab())
        return item_id
    def add_decoration(self, loc, item_type):
        self.add_object(Map_object_item(loc, item_type))
    def random_clear_tiles(self,chance,x_range,y_range):
        for y in y_range:
            for x in x_range:
                if random() < chance and not ui.mtctl.blocking(self.current_map_get_element(x,y)):
                    yield(x,y)
    def add_object(self, obj):
        self.objects.append(obj)
        return len(self.objects)-1
    # Replace with a generic remove_object
    def remove_enemy(self, enemy_id):
        self.objects[enemy_id] = None
    def remove_item(self, item_id):
        self.objects[item_id] = None
    # Replace with a generic add_object_event
    def add_enemy_event(self, enemy_id, event):
        self.objects[enemy_id].attach_event(event)
    def add_item_event(self, item_id, event):
        self.objects[item_id].attach_event(event)

#####################################################################
# Library                                                           #
#####################################################################
    def map_setup_icy_mountains(self):
        ###############################
        # ICE TEMPLE                  #
        ###############################
        # star = [[False for y in range(10)] for x in range(10)]
        # def ice_temple_shader():
        #     stars = ["star 3", "star 4", "star 7", "star 9"]
        #     # Expected star lifetime          = t = 25
        #     # Expected stable number of stars = n =  5
        #     # k1 = 1/t = 1/25 = 0.04
        #     # n/(100-n) = k2/k1
        #     # k2 \approx k1 n / 100 = 0.04 * 5 / 100 = 0.002
        #     for y in range(10):
        #         for x in range(10):
        #             if star[x][y]:
        #                 ui.render_item(ui.map_viewport, ((20+x)*32,y*32), star[x][y])
        #                 if random() < 0.04:
        #                     star[x][y] = None
        #             else:
        #                 if random() < 0.002:
        #                     star[x][y] = choice(stars)
        # FIXME: restore shader support
        # wv.shader = lambda: ice_temple_shader()
        self.wormhole((3,3),"tower level 3",(4,4))
        # Add decorations
        self.add_decoration((2,2),"magical symbol R")
        self.add_decoration((4,2),"magical symbol G")
        self.add_decoration((1,3),"magical symbol Y")
        self.add_decoration((5,3),"magical symbol R")
        self.add_decoration((2,4),"magical symbol G")
        self.add_decoration((4,4),"magical symbol Y")
        self.add_decoration((3,3),"magical symbol Y")

        ###############################
        # ICY MOUNTAINS               #
        ###############################
        for (x,y) in self.random_clear_tiles(0.2,range(10,20),range(0,10)):
            self.add_enemy((x,y),"ice",choice(ice_enemies),[('kanji',300)],1)
        for (x,y) in self.random_clear_tiles(0.2,range(0,20),range(10,20)):
            self.add_enemy((x,y),"ice",choice(ice_enemies),[('kanji',300)],1)
        for (x,y) in self.random_clear_tiles(0.3,range(20,50),range(0,20)):
            self.add_enemy((x,y),"ice",choice(ice_enemies),[('kanji',300)],1)
        def ice_quest():
            ui.change_text([U"You've got a red spellbook."])
            mhc.gain_item("spellbook red 9")
            mhc.quest_do("ice artifact")
        if not mhc.quest_is_done("ice artifact"):
            self.add_item((45,6),"spellbook red 9",ice_quest)

#####################################################################
# FIXME: Parts of the quest code assume that they will be           #
#        restarted on chara's entry.                                #
# And there may be some namespace collisions                        #
#####################################################################
    def map_setup_world(self):
        ###############################
        # WORMHOLES                   #
        ###############################
        self.wormhole((7,8),"castle",(4,8))
        self.wormhole((33,34), "library", (5,8))
        self.wormhole((38,34), "wizard shop", (5,8))
        self.wormhole((35,37), "angel sanctuary", (5,1))
        self.wormhole((41,37), "blacksmith", (5,1))
        self.wormhole((2,36),"hospital",(5,8)) # Hospital wormhole

        ###############################
        # CASTLE SOLDIERS AND EVENTS  #
        ###############################
        # The castle has many soldiers
        self.add_chara("soldier-axe",route=[(9,15),(1,15),(1,16),(2,16),(2,10),(2,16),(1,16),(1,15)])
        self.add_chara("soldier-axe",route=[(9,10),(9,13),(4,13),(4,10)])
        self.add_chara("soldier-axe",route=[(18,15),(18,16),(17,16),(17,10),(17,16),(18,16),(18,15),(10,15)])
        self.add_chara("soldier-axe",route=[(10,10),(10,13),(15,13),(15,10)])

        self.add_chara("soldier-axe",route=[(2,1),(2,9),(2,1),(1,1),(1,2),(9,2),(1,2),(1,1)])
        # The building blocks this route, but it still works:
        self.add_chara("soldier-axe",route=[(4,4),(9,4),(9,9),(4,9)])
        self.add_chara("soldier-axe",route=[(17,1),(17,9),(17,1),(18,1),(18,2),(10,2),(18,2),(18,1)])
        # The building blocks this route, but it still works:
        self.add_chara("soldier-axe",route=[(15,9),(15,4),(10,4),(10,9)])

        def open_castle_gate():
            if mhc.quest_is_done("castle gate open"): return
            ui.change_text([U"Oh, you're a hero. Please come in."])
            self.change_tile((6,16),'k')
            # Take the blue book away maybe ?
            mhc.quest_do("castle gate open")

        def castle_gate_checkup():
            if mhc.quest_is_done("castle gate open"): return
            if mhc.quest_is_done("desert artifact") and mhc.quest_is_done("magic sword complete"):
                open_castle_gate()
            else:
                ui.change_text([
                    U"We're looking for a hero to face kanji monsters.",
                    U"But too many brave souls failed already.",
                    U"Come back once you get a magic sword and a spellbook",
                ])

        if mhc.quest_is_done("castle gate open"):
            self.change_tile((6,16),'k')
        else:
            self.add_enter_event((6,17), lambda: castle_gate_checkup())
        ###############################
        # ELVEN GATE                  #
        ###############################
        def open_elven_gate():
            self.change_tile((23,36),'k')
        # REFACTORME: It worked fine when it was recomputed every time
        #             player got close to the game. Is it still ok now ?
        # Was it open originally ?
        gate_was_open = mhc.quest_is_done("elven gate tax")
        def elven_gate_soldier_event():
            if gate_was_open:
                ui.change_text([U"Welcome to the Elven town."])
            else:
                if mhc.quest_is_done("elven gate tax"):  return
                if mhc.has_money(2):
                    mhc.take_money(2)
                    mhc.quest_do("elven gate tax")
                    open_elven_gate()
                    ui.change_text([U"OK, you may come in now."])
                else:
                    ui.change_text([
                        U"You must pay a one-time 2 coins tax to pass.",
                        U"There's certainly some cash in the forest southwards.",
                        U"Just watch for the monsters."])
        self.add_chara("soldier-elf",route=[(22,35),(22,38)], event=elven_gate_soldier_event)
        if mhc.quest_is_done("elven gate tax"): open_elven_gate()
        self.add_chara("soldier-elf",route=[(26,32),(26,37),(26,32),(23,31)])
        ###############################
        # ELVEN BRIDGE                #
        ###############################
        # There used to be a level test
        # but now it's just a nice way to skip useless kana part
        def open_bridge():
            self.change_tile((46,31),'.')
        def elven_bridge_check_xp():
            if mhc.quest_is_done("elven bridge ok"):
                return
            ui.change_text([
                    U"The inexperienced should not cross the bridge, it's too dangerous.",
                    U"If you know how to beat the kana demons, you may go ahead.",
                    U"Otherwise, train some on the Dwarven hills.",
                    U"The hills are located south from here."
            ])
            mhc.quest_do("elven bridge ok")
            open_bridge()
        def bridge_soldier_event():
            if bridge_was_ok:
                ui.change_text([U"If the demons on the other side are too hard,",
                                U"you may want to try with the easy ones on the Dwarven hills.",
                                U"The hills are located south from here."
                              ])
            else:
                elven_bridge_check_xp()
        if mhc.quest_is_done("elven bridge ok"):
            open_bridge()
        bridge_was_ok = mhc.quest_is_done("elven bridge ok")
        self.add_chara("soldier-elf",route=[(45,32),(47,32)],event=bridge_soldier_event)
        ###############################
        # OASIS                       #
        ###############################
        def arab_trader_quest():
            if mhc.quest_is_done("antiheat potion complete"):
                ui.change_text([U"So you've drunk the potion.", U"You may go to the desert now."])
            else:
                ui.change_text([
                    U"The desert east of here is so hot.",
                    U"You will quickly collapse unless you've drunk a mushroom potion.",
                    U"Unfortunately I have no idea what kinds of mushrooms are needed.",
                    U"Ask around in the Elven town maybe."
                ])
                mhc.quest_do("antiheat potion idea")
        self.add_chara("arab-trader",route=[(44,13),(46,13)], event=arab_trader_quest)

        ###############################
        # ELVEN TRADER                #
        ###############################
        self.add_chara("elf-trader",route=[(3,23), (3,24)], event=lambda: ui.change_text([
                U"Many animals and people have been possessed by kanji demons.",
                U"You may kill the demons by shouting their names.",
                U"I would do that myself, but there are too many names to remember.",
                U"Maybe you should visit the Elven town, it's south east from here."]))

        ###############################
        # FOREST 1                    #
        ###############################
        for (x,y) in self.random_clear_tiles(0.1,range(0,10),range(40,50)):
            self.add_enemy((x,y),'forest',choice(forest_enemies),['hiragana'],1)
        for (x,y) in self.random_clear_tiles(0.05,range(10,30),range(40,50)):
            self.add_enemy((x,y),'forest',choice(forest_enemies),['hiragana'],1)
        self.add_item((1,41),"copper coins", lambda: mhc.receive_money(1))
        self.add_item((1,45),"copper coins", lambda: mhc.receive_money(1))
        ###############################
        # DWARVEN HILLS               #
        ###############################
        for (x,y) in self.random_clear_tiles(0.1,range(30,50),range(40,60)):
            self.add_enemy((x,y),'hills',choice(mountain_enemies),['hiragana','katakana'],1)
        for (x,y) in self.random_clear_tiles(0.02,range(30,50),range(40,60)):
            self.add_item((x,y),"copper coins", lambda: mhc.receive_money(1))

        ###############################
        # MEADOW                      #
        ###############################
        def meadow_quest():
            ui.change_text([U"You've found the magic sword but it's broken."])
            mhc.gain_item("broken sword")
            mhc.quest_do("broken sword complete")
        if not mhc.quest_is_done("broken sword complete"):
            self.add_item((21,56),"broken sword", meadow_quest)

        ###############################
        # CAVE ENTRANCE               #
        ###############################
        self.wormhole((61,37),"cave",(1,7))





        ###############################
        # FOREST 2                    #
        ###############################
        def add_random_forest_mushrooms(x,y):
            rmush = choice(mushroom_forest_decoration_mushrooms)
            if mhc.quest_is_done("antiheat potion recipe"):
                if rmush == "yellow mushroom" and not mhc.quest_is_done("antiheat potion yellow"):
                    item = self.add_item((x,y), rmush)
                    self.add_item_event(item, lambda: get_mushroom_yellow(item))
                elif rmush == "green mushroom 2" and not mhc.quest_is_done("antiheat potion bgreen"):
                    item = self.add_item((x,y), rmush)
                    self.add_item_event(item, lambda: get_mushroom_bgreen(item))
                else:
                    self.add_decoration((x,y),rmush)
            else:
                self.add_decoration((x,y),rmush)
        def get_mushroom_yellow(item):
            if not mhc.quest_is_done("antiheat potion yellow"):
                # Already got some other mushrooms of the same type
                self.remove_item(item)
                mhc.gain_item("yellow mushroom")
                mhc.quest_do("antiheat potion yellow")
                ui.change_text([
                    U"You've got yellow mushrooms.",
                    U"You need yellow and bright green mushrooms for the potion."])
        def get_mushroom_bgreen(item):
            if not mhc.quest_is_done("antiheat potion bgreen"):
                # Already got some other mushrooms of the same type
                self.remove_item(item)
                mhc.gain_item("green mushroom 2")
                mhc.quest_do("antiheat potion bgreen")
                ui.change_text([
                    U"You've got bright green mushrooms.",
                    U"You need yellow and bright green mushrooms for the potion."])
        for (x,y) in self.random_clear_tiles(0.1,range(20,40),range(10,30)):
            self.add_enemy((x,y),'marsh',choice(forest_enemies),['hiragana','katakana','kanaword'],1)
        # FIXME: new mushrooms will grow only if you leave the forest
        # To make it less annoying, let's double number of mushrooms
        for (x,y) in self.random_clear_tiles(0.1,range(20,40),range(10,30)):
            add_random_forest_mushrooms(x,y)
        ###############################
        # DESERT                      #
        ###############################
        # Desert quest
        def desert_quest():
            ui.change_text([U"You've got a spellbook."])
            mhc.gain_item("spellbook blue 9")
            mhc.quest_do("desert artifact")
        if not mhc.quest_is_done("desert artifact"):
            self.add_item((61,11),"spellbook blue 9",desert_quest)
        # Desert enemies
        for (x,y) in self.random_clear_tiles(0.1,range(50,60),range(10,20)):
            self.add_enemy((x,y),'desert',choice(desert_enemies),['kanaword',('kanji',100)],1)
        for (x,y) in self.random_clear_tiles(0.2,range(50,70),range(20,30)):
            self.add_enemy((x,y),'desert',choice(desert_enemies),['kanaword',('kanji',100)],1)
        for (x,y) in self.random_clear_tiles(0.2,range(60,70),range(10,20)):
            self.add_enemy((x,y),'desert',choice(desert_enemies),['kanaword',('kanji',100)],1)
        # Desert decorations
        self.add_decoration((57,23),"skeleton 3")
        self.add_decoration((55,11),"bones")
        self.add_decoration((51,17),"skull")
        self.add_decoration((63,16),"skull")
        self.add_decoration((65,14),"skeleton 5")
        self.add_decoration((61,24),"skeleton 1")
        # Desert heat
        def desert_heat():
            if not mhc.quest_is_done("antiheat potion complete"):
                if random() < 0.25:
                    ui.change_text([U"The heat is too strong.", U"You lost 1 HP."])
                    mhc.damage(1)
                else:
                    ui.change_text([U"The heat is too strong.", U"Maybe you should return already."])
        if not mhc.quest_is_done("antiheat potion complete"):
            for y in range(10,30):
                for x in range(50,70):
                    self.add_enter_event((x,y),lambda:desert_heat())

class World_view:
    def __init__(self):
        self.surface_cache = pygame.Surface((320,320))
        self.surface_cache_valid = False

        self.shader = None

        # This is a cache of prerendered tiles
        self.prerendered_tiles = []
        # This structure maps (center, ul, ur, ll, lr) tuples to ids in self.prerendered_tiles
        # It is used only from prerender_tiles()
        self.prerender_ht = {}
        # This structure maps tile numbers to prerendered tiles
        self.prerender_cache = []

        self.prerender_cache_valid = False
    def switch_map_event(self, (x,y)):
        self.max_shift_y = 32 * (len(wm.current_map) - 10)
        longest_line = 0
        for line in wm.current_map:
            longest_line = max(longest_line, len(line))
        self.max_shift_x = 32 * (longest_line - 10)

        self.center_at((x*32, y*32))

        self.prerender_cache_valid = False
    def center_at(self, (x,y)):
        self.shift_x = x - 5*32
        self.shift_y = y - 5*32
        if self.shift_x < 0: self.shift_x = 0
        if self.shift_y < 0: self.shift_y = 0
        if self.shift_x > self.max_shift_x : self.shift_x = self.max_shift_x
        if self.shift_y > self.max_shift_y : self.shift_y = self.max_shift_y

    # Call every time tile data changes
    def prerender_cache_execute(self):
        self.prerender_cache_valid = True
        self.prerender_cache = [[None for tile in line] for line in wm.current_map]
        for y in range(len(self.prerender_cache)):
            for x in range(len(self.prerender_cache[y])):
                ul = None
                ur = None
                ll = None
                lr = None
                this = wm.current_map_get_element(x, y)
                if corner_shader.has_key(this):
                    r = wm.current_map_get_element(x+1,y  )
                    d = wm.current_map_get_element(x,  y+1)
                    l = wm.current_map_get_element(x-1,y)
                    u = wm.current_map_get_element(x,  y-1)
                    for (horz, vert, diag, shade_to) in corner_shader[this]:
                        if( r in horz and
                            d in vert and
                            ((not diag) or (wm.current_map_get_element(x+1,y+1) in diag))):
                            lr = shade_to
                            break
                    for (horz, vert, diag, shade_to) in corner_shader[this]:
                        if( r in horz and
                            u in vert and
                            ((not diag) or (wm.current_map_get_element(x+1,y-1) in diag))):
                            ur = shade_to
                            break
                    for (horz, vert, diag, shade_to) in corner_shader[this]:
                        if( l in horz and
                            d in vert and
                            ((not diag) or (wm.current_map_get_element(x-1,y+1) in diag))):
                            ll = shade_to
                            break
                    for (horz, vert, diag, shade_to) in corner_shader[this]:
                        if( l in horz and
                            u in vert and
                            ((not diag) or (wm.current_map_get_element(x-1,y-1) in diag))):
                            ul = shade_to
                            break
                key = (this, ul, ur, ll, lr)
                if self.prerender_ht.has_key(key):
                    self.prerender_cache[y][x] = self.prerender_ht[key]
                else:
                    cache_line_id = len(self.prerendered_tiles)
                    self.prerendered_tiles.append(pygame.Surface((32,32)))
                    ui.render_tile(self.prerendered_tiles[cache_line_id], (0, 0), this)
                    if ul:
                        self.prerendered_tiles[cache_line_id].blit(ui.mtctl.corners[ul][0], ( 0, 0))
                    if ur:
                        self.prerendered_tiles[cache_line_id].blit(ui.mtctl.corners[ur][1], (16, 0))
                    if ll:
                        self.prerendered_tiles[cache_line_id].blit(ui.mtctl.corners[ll][2], ( 0,16))
                    if lr:
                        self.prerendered_tiles[cache_line_id].blit(ui.mtctl.corners[lr][3], (16,16))
                    self.prerender_ht[key] = cache_line_id
                    self.prerender_cache[y][x] = cache_line_id
    def render(self):
        if not self.prerender_cache_valid:
            self.prerender_cache_execute()
        # This only caches the background
        if not self.surface_cache_valid:
            minx=(self.shift_x)/32
            maxx=(self.shift_x+319)/32
            miny=(self.shift_y)/32
            maxy=(self.shift_y+319)/32
            for y in range(miny,maxy+1):
                for x in range(minx,maxx+1):
                    if y < 0 or y >= len(self.prerender_cache) or x < 0 or x >= len(self.prerender_cache[y]):
                        # This is black tile
                        self.surface_cache.fill((0, 0, 0), (32*x-self.shift_x, 32*y-self.shift_y, 32, 32))
                    else:
                        cache_line_id = self.prerender_cache[y][x]
                        self.surface_cache.blit(self.prerendered_tiles[cache_line_id], (32*x-self.shift_x, 32*y-self.shift_y))

        ui.map_viewport.blit(self.surface_cache, (0,0))
        # First act enemies, then items
        # But, first blit items, then enemies, so reversed(self.objects)
        # reversed() is available only in Python 2.4+
        # Let's do it by hand for 2.3-compatibility
        for o_id in range(len(wm.objects)):
            o = wm.objects[len(wm.objects) - 1 - o_id]
            if o != None:
                o.render()
        for chara in wm.charas:
            chara.render()
        # REFACTORME: Bring shader support back
        # if self.shader:
        #    self.shader()

# FIXME: map_setup used to have keep_textbox field, for hospital mostly what should we do with it ?

###########################################################
# Global tile controllers                                 #
###########################################################
cheat_quest = [
    1,
    "elven gate tax",
    "elven bridge ok",
    "antiheat potion idea",
    "antiheat potion recipe",
    "antiheat potion yellow",
    "antiheat potion bgreen",
    "antiheat potion complete",
    "desert artifact",
    "broken sword complete",
    "sword complete",
    "blue crystals complete",
    "magic sword complete",
    "castle gate open",
    "ice artifact",
    "dungeon gate open",
    "treasure 1",
    "treasure 2",
    "treasure 3",
    "treasure 4",
    "treasure 5",
    "treasure 6",
    "treasure 7",
    "treasure 8",
    "treasure 9",
    "treasure 10",
    "treasure 11",
    "treasure 12",
    "treasure 13",
    "treasure 14",
    "treasure 15",
    "treasure 16",
    "treasure 17",
    "treasure 18",
    "treasure 19",
    "treasure 20",
]
mountain_enemies = [
    "spotty lizard",
    "red lizard",
    "brown lizard",
    "black lizard",
    "green lizard",
    "red scoprion",
    "yellow scoprion",
    "gray scoprion",
    "blue scoprion",
    "brown scoprion",
    "black scoprion",
]
forest_enemies = [
    "white rat",
    "black rat",
    "brown rat",
    "red rat",
    "white rat",
    "black rat",
    "brown rat",
    "red rat",
    "green turtle",
    "red turtle",
    "black turtle",
    "brown turtle",
    "blue turtle",
    "yellow turtle",
]
desert_enemies = [
    "red scoprion",
    "yellow scoprion",
    "gray scoprion",
    "blue scoprion",
    "brown scoprion",
    "black scoprion",
    "vulture 1",
    "vulture 2",
    "vulture 3",
]
ice_enemies = [
    "eagle 1",
    "eagle 1",
    "eagle 2",
    "eagle 2",
    "eagle 3",
    "eagle 3",
    "eagle 4",
    "eagle 4",
    "bear 1",
    "bear 1",
    "bear 2",
    "bear 2",
    # Only  dogs in the right color
    "dog 3",
    "dog 3",
    "dog 4",
    "dog 4",
    "dog 5",
    "dog 5",
    # Only ice dragons
    "dragon tiny 3",
    "dragon tiny 3",
    "dragon small 3",
    "dragon small 3",
    # big dragons should be less likely than other enemies
    "dragon normal 3",
    "dragon big 3",
]
mushroom_forest_decoration_mushrooms = [
    "black mushroom",
    "white mushroom",
    "gray mushroom",
    "orange mushroom",
    "red mushroom",
    "green mushroom",
    "blue mushroom",
    "Dbrown mushroom",
    "black mushroom 2",
    "gray mushroom 2",
    "violet mushroom",
    "yellow mushroom",
    "red mushroom 2",
    "green mushroom 2",
    "cyan mushroom",
    "Lbrown mushroom",
]


###########################################################
# Main                                                    #
###########################################################

try:
    mistakes = Mistakes()
    chapter_factory = Chapter_factory()
    list_of_vocabulary = {
        'katakana' : 'data/demons-katakana.txt',
        'hiragana' : 'data/demons-hiragana.txt',
        'kanaword' : 'data/demons-kanawords.txt',
        'traduction' : 'data/demons-kanawords.txt',
        'kanji' : 'data/demons-kanji.txt',
    }

    book = Book_of_demons(chapter_factory, list_of_vocabulary)
    mhc  = Main_Hero_Controller()
    wm   = World_model()
    wv   = World_view()
    ui   = UI()

    main_hero = Chara("female-blue", position=(0, 0))
    main_hero.is_main = True # This isn't a particularly nice hack, subclass maybe ?

    wm.switch_map("world", (14,25))

    ui.change_text([U"Welcome to the 日本語RPG", U"", U"Press F1 for quick help"])

    ui.main_loop()
except SystemExit: # Weird exception on Windows
    pass
except Exception:
    util.save_errormsg(sys.exc_info())
    raise
