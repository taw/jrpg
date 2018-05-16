#!/usr/bin/python
# -*- coding: UTF-8 -*-

from __future__ import print_function
import warnings
import sys, pygame, pickle, re, traceback
from math import sqrt, floor
from random import *

# Import other jrpg modules
import images

pygame.display.init()
pygame.display.set_caption("JRPG - new world UI demo")
pygame.font.init()

font_paths = ["/usr/share/fonts/kochi-substitute/kochi-gothic-subst.ttf"]

# Directory where all the images are, trailing / is needed
images_dir = "images/"

full_screen_mode = False # True

main_chara_speed =  4
xp_per_kanji =  3

###########################################################
# A few helpful functions                                 #
###########################################################
def set_sym_diff(set1, set2):
    d = {}
    ds2 = []
    for i in set1:
        d[i] = 1
    for i in set2:
        if i in d:
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
def sgn(x):
    if x > 0:
        return +1
    elif x == 0:
        return 0
    else:
        return -1

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
# This class manages the common part of the UI            #
###########################################################
class UI:
    def __init__(self):
        mtctl_terrain = images.mtctl_terrain
        mtctl_enemies = images.mtctl_enemies
        mtctl_items   = images.mtctl_items
        ctdir         = images.ctdir
        battle_bg     = images.battle_bg

        global full_screen_mode
        self.clock    = pygame.time.Clock()
        size = (width, height) = 640, 480
        self.text     = []
        if full_screen_mode:
            self.screen = pygame.display.set_mode(size, pygame.DOUBLEBUF|pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(size, pygame.DOUBLEBUF)
        font_set = False
        for font_path in font_paths:
            try:
                self.font     = pygame.font.Font(font_path, 18)
                self.font_med = pygame.font.Font(font_path, 40)
                self.font_big = pygame.font.Font(font_path, 64)
                font_set = True
                break
            # This IOError object is behaving strangely
            # It does not have strerror and can't be unpacked to (errno, strerror) tuple,
            # unlike a regular IOError
            except IOError as e:
                print("Opening font at %s failed: %s" % (font_path, e))
        if not font_set:
            print("Font file not found")
            sys.exit(1)
        self.key = [False for i in range(512)]
        self.mtctl = Map_Tiles_Controller(images_dir+"angband.png", mtctl_terrain, mtctl_enemies, mtctl_items)
        self.chara_tiles_dir = {}
        for k in ctdir:
            self.chara_tiles_dir[k] = pygame.image.load(images_dir+ctdir[k]).convert_alpha()
        self.text_cache = self.screen.subsurface(pygame.Rect((0,320),(640,160)))
        self.text_cache_valid = False
    def tick(self):
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
            #print self.clock.get_fps()
    def key_down(self, key):
        self.key[key] = True
    def key_up(self, key):
        self.key[key] = False
    def key_pressed(self, key):
        return(self.key[key])
    def change_text(self, new_text, new_text_color=(0,255,0)):
        self.text = [(t, new_text_color) for t in new_text]
        self.text_cache_valid = False
    def append_text(self, new_text, new_text_color=(0,255,0)):
        self.text = self.text + [(t, new_text_color) for t in new_text]
        # Save only the last 5 lines, if there are too many
        if len(self.text) > 5:
            self.text = self.text[len(self.text)-5:len(self.text)]
        self.text_cache_valid = False
    def blit_text(self):
        if not self.text_cache_valid:
            self.text_cache.fill((0,0,0))
            self.render_text_multicolor(self.text_cache, self.font, self.text, (32,32), (0,0), 24)
            self.text_cache_valid = True
        # No need to blit, as it's a subsurface
        #ui.screen.blit(self.text_cache, (0,320))
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
    def render_furi(self, target, furicode, xy, font_info,
                    font_furi, color_base, color_furi, display_all_furi):
        # No space for too many characters
        (x,y) = xy
        (size_limit,font_main,font_subst) = font_info
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
    def blit_tile(self, target, target_rect, tile_id):
        source_rect = self.mtctl.ttt[tile_id][0]
        target.blit(self.mtctl.img, target_rect, source_rect)
    def blit_enemy(self, target_rect, enemy_id):
        source_rect = self.mtctl.ett[enemy_id]
        self.screen.blit(self.mtctl.img, target_rect, source_rect)
    def blit_item(self, target_rect, item_id, target=None):
        source_rect = self.mtctl.itt[item_id]
        if target == None:
            target = self.screen
        target.blit(self.mtctl.img, target_rect, source_rect)
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
        self.xpfor  = {} # \in {None, 0, 1, 2, 3}
        self.quests = {}
        self.money  = 0
        self.inventory = []
        # Should be in some UI class
        self.stats_cache = pygame.Surface((320, 160))
        self.stats_cache_valid = False
    # This code works in battle mode and in worldmap mode
    def blit_statistics(self):
        if not self.stats_cache_valid:
            self.stats_cache.fill((0,0,0))
            ui.render_text_unicolor(self.stats_cache, ui.font, [
                        "Level: %d" % self.level,
                        "XP:    %d" % self.xp,
                        "HP:    %d/%d" % (self.hp, self.hpmax),
                        "Money: %d euro" % self.money,
                        ],
                        (32, 32), (0,0), (0, 255, 0), 24)
            for i in range(len(self.inventory)):
                ui.blit_item((32+i*32,32+24*4), self.inventory[i], self.stats_cache)
            self.stats_cache_valid = True
        ui.screen.blit(self.stats_cache, (320, 0))
###########################################################
# This class controls a single map object                 #
###########################################################
class Map_object:
    def __init__(self, bbox, blit, event):
        self.bbox  = bbox
        self.blit  = blit
        self.event = event
# There should be priorities for both blit and event

###########################################################
# This class controls the current map                     #
###########################################################
class Map:
    # self.m is (-1..n), not (0..n-1)
    # Never access it directly, unless you do +1
    def __init__(self, ui):
        self.ui = ui
        self.surface_cache = pygame.Surface((320,320))
        self.setup()
    def setup(self,new_m=None,new_charas=[]):
        self.m            = new_m
        self.charas       = new_charas
        self.chara_events = {}
        self.objects      = []
        self.shader       = None
        self.enter_events = {}
        self.surface_cache_valid = False
    def change_tile(self, xy, new_value):
        (x,y) = xy
        self.m[y+1][x+1] = new_value
        self.surface_cache_valid = False
    def get_element(self,x,y):
        # Translate from abstract map coords to self.m coordinates
        x = x+1
        y = y+1
        if y<0:
            y = 0
        if y>=len(self.m):
            y = len(self.m) - 1
        if x<0:
            x = 0
        if x>=len(self.m[y]):
            x=len(self.m[y])-1
        return self.m[y][x]
    # They're identical modulo blit priority
    def add_enemy(self, enemy_pos, enemy_sprite):
        (x,y) = enemy_pos
        def blit():
            self.ui.blit_enemy((32*x,32*y), enemy_sprite)
        bbox = pygame.Rect((x*32,y*32),(32,32))
        o    = Map_object(bbox, blit, None)
        self.objects.append(o)
        return len(self.objects)-1
    def add_item(self, item_pos, item_class):
        (x,y) = item_pos
        def blit():
            self.ui.blit_item((32*x,32*y), item_class)
        bbox = pygame.Rect((x*32,y*32),(32,32))
        o    = Map_object(bbox, blit, None)
        self.objects.append(o)
        return len(self.objects)-1
    # Replace with a generic remove_object
    def remove_enemy(self, enemy_id):
        self.objects[enemy_id] = None
    def remove_item(self, item_id):
        self.objects[item_id] = None
    # Replace with a generic add_object_event
    def add_enemy_event(self, enemy_id, event):
        self.objects[enemy_id].event = event
    def add_item_event(self, item_id, event):
        self.objects[item_id].event = event
    # return True if collides, False if the way is free
    def collides(self, rect):
        # Convert rect from pixelspace to tilespace
        top    = rect.top    >> 5
        left   = rect.left   >> 5
        bottom = rect.bottom >> 5
        right  = rect.right  >> 5
        for i in range(top, bottom+1):
            for j in range(left, right+1):
                if self.ui.mtctl.blocking(self.get_element(j,i)):
                    return True
        return False
    def collides_with(self, rect, x, y):
        # Convert rect from pixelspace to tilespace
        top    = rect.top    >> 5
        left   = rect.left   >> 5
        bottom = rect.bottom >> 5
        right  = rect.right  >> 5
        return (x >= left and x <= right and y >= top and y <= bottom)
    def add_chara(self, chara):
        self.charas.append(chara)
    def run_charas(self):
        for chara in self.charas:
            chara.patrol()
    # self is not really used
    def pixel_rect_to_tile_rect(self, pixel_rect):
        top    = pixel_rect.top >> 5
        left   = pixel_rect.left >> 5
        bottom = pixel_rect.bottom >> 5
        right  = pixel_rect.right >> 5
        return pygame.Rect(left,top,right-left+1,bottom-top+1)
    # These are for the main chara only
    def add_enter_event(self, tile, event):
        if tile not in self.enter_events:
            self.enter_events[tile] = []
        self.enter_events[tile].append(event)
    # Convenience methods
    def add_enter_event_edge_north(self, event):
        for x in range(10):
            self.add_enter_event((x, -1), event)
    def add_enter_event_edge_south(self, event):
        for x in range(10):
            self.add_enter_event((x, 10), event)
    def add_enter_event_edge_west(self, event):
        for y in range(10):
            self.add_enter_event((-1, y), event)
    def add_enter_event_edge_east(self, event):
        for y in range(10):
            self.add_enter_event((10, y), event)
    # This sucks - I can't decide whether there may be
    # only a single event, or more events are possible
    # Let's say that for now all events are "map changing events",
    # and they block other old-map's events from happening
    def add_chara_event(self, chara, event):
        self.chara_events[chara] = event
    def enter_event(self, tile):
        if tile in self.enter_events:
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
            if o != None and o.event != None:
                if pygame.Rect(new_pos,(24,24)).colliderect(o.bbox):
                    o.event()
                    return
    def collides_with_chara(self, pos, chara):
        return pygame.Rect(pos,(24,24)).colliderect(pygame.Rect(chara.pos,(24,24)))
    def blit(self):
        if not self.surface_cache_valid:
            self.surface_cache_valid = True
            for i in range(len(self.m)-2):
                for j in range(len(self.m[i])-2):
                    self.ui.blit_tile(self.surface_cache, (32*j,32*i), self.get_element(j,i))
            # OK, so we have the first approximation. Now let the fun begin :-D
            # (this, hor, vert, diag, shade)
            # None if doesn't matter (diagonal)
            any = [' ', 's', 'h', '.', ',', 'D', 'd', 'V', 'k', '_', 'H', '>', '<', ':', 't', 'T', 'm', 'r', '~', 'P', 'C', 'i', 'j', 'b', 'S', 'W', 'B', 'K', 'z', 'Z', 'M', 'Q', 'E', 'x', 'X']
            grs = [' ', 'r', 't', 'T', 'h']
            corner_shader = [
                          (' ', '.', '.', any, '.'),
                          ('.', grs, grs, grs, ' '),
                          ('h', ' ', ' ', ' ', ' '),
                          (' ', 'h', 'h', 'h', 'h'),
                         ]
            for i in range(len(self.m)-2):
                for j in range(len(self.m[i])-2):
                    for (this, horz, vert, diag, shade_to) in corner_shader:
                        if(self.get_element(j,  i  ) in this and
                           self.get_element(j+1,i  ) in horz and
                           self.get_element(j,  i+1) in vert and
                           self.get_element(j+1,i+1) in diag):
                            self.surface_cache.blit(ui.mtctl.corners[shade_to][3], (32*j+16,32*i+16))
                            break
                    for (this, horz, vert, diag, shade_to) in corner_shader:
                        if(self.get_element(j,  i  ) in this and
                           self.get_element(j+1,i  ) in horz and
                           self.get_element(j,  i-1) in vert and
                           self.get_element(j+1,i-1) in diag):
                            self.surface_cache.blit(ui.mtctl.corners[shade_to][1], (32*j+16,32*i))
                            break
                    for (this, horz, vert, diag, shade_to) in corner_shader:
                        if(self.get_element(j,  i  ) in this and
                           self.get_element(j-1,i  ) in horz and
                           self.get_element(j,  i+1) in vert and
                           self.get_element(j-1,i+1) in diag):
                            self.surface_cache.blit(ui.mtctl.corners[shade_to][2], (32*j,32*i+16))
                            break
                    for (this, horz, vert, diag, shade_to) in corner_shader:
                        if(self.get_element(j,  i  ) in this and
                           self.get_element(j-1,i  ) in horz and
                           self.get_element(j,  i-1) in vert and
                           self.get_element(j-1,i-1) in diag):
                            self.surface_cache.blit(ui.mtctl.corners[shade_to][0], (32*j,32*i))
                            break

        ui.screen.blit(self.surface_cache, (0,0))
        # First act enemies, then items
        # But, first blit items, then enemies, so reversed(self.objects)
        # reversed() is available only in Python 2.4+
        # Let's do it by hand for 2.3-compatibility
        for o_id in range(len(self.objects)):
            o = self.objects[len(self.objects) - 1 - o_id]
            if o != None:
                if o.blit != None:
                    o.blit()
        for chara in self.charas:
            chara.blit()
        if self.shader:
            self.shader()
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
    def __init__(self,ui,m,chara_class,position=None,route=None):
        self.ui      = ui
        self.m       = m
        self.img     = ui.chara_img(chara_class)
        self.dt      = Chara.Sprite_down
        self.step    = 0
        self.spp     = 0
        self.is_main = False
        if position and route:
            raise Exception("Trying to set chara position both as position and as route")
        if not position and not route:
            raise Exception("Chara position not seit as either position or route")
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
    def move_blocked(self, new_pos):
        if self.m.collides(pygame.Rect(new_pos[0], new_pos[1], 24, 24)):
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
            self.m.move_events(old_pos, new_pos)
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
    def blit(self):
        # Chara location on the ground is 24x24 square
        # 8 bits above it should simply be ignored
        if self.step == 3:
            s = 1
        else:
            s = self.step
        ui.screen.blit(self.img, (self.pos[0],self.pos[1]-8), pygame.Rect(24 * s, 32 * self.dt, 24, 32))

###########################################################
# This class controls the map switching                   #
# For "controversial reasons" it knows about shape of the #
# world                                                   #
###########################################################
class World:
    def __init__(self,ui):
        self.ui    = ui
        self.m     = Map(ui)
        f = open("map.txt")
        self.tiles = f.readlines()
        f.close()
        # Move as much info as possible from setup routines to these tuples
        self.map_directory = {
            (0,3) : (self.map_setup_0_3, U"By the hospital"),
        }
    def parse_map_passage(self, tile, n):
        if tile == 'x':
            return -1
        elif tile == '^':
            return n
        elif ord(tile) >= ord('0') and ord(tile) <= ord('9'):
            return ord(tile) - ord('0')
        else:
            raise Exception("Illegal map passage code " + tile)
    def map_setup(self, m, tele, keep_textbox=False):
        (mx,my) = m
        (tele_x,tele_y) = tele
        global main_hero
        (add_events,map_title) = self.map_directory[(mx,my)]
        tiles = submatrix(self.tiles, mx*13, my*12, 12, 12)
        # Setup passages to other maps
        self.m.setup(tiles,[])
        # North
        for x in range(10):
            tile = self.parse_map_passage(tiles[0][x+1], x)
            if tile != -1:
                self.m.add_enter_event(Ne(x), (lambda xb: lambda: self.map_setup((mx,my-1), S(xb)))(tile))
                self.m.change_tile((x,-1),'X')
        # South
        for x in range(10):
            tile = self.parse_map_passage(tiles[11][x+1], x)
            if tile != -1:
                self.m.add_enter_event(Se(x), (lambda xb: lambda: self.map_setup((mx,my+1), N(xb)))(tile))
                self.m.change_tile((x,10),'X')
        # West
        for y in range(10):
            tile = self.parse_map_passage(tiles[y+1][0], y)
            if tile != -1:
                self.m.add_enter_event(We(y), (lambda yb: lambda: self.map_setup((mx-1,my), E(yb)))(tile))
                self.m.change_tile((-1,y),'X')
        # East
        for y in range(10):
            tile = self.parse_map_passage(tiles[y+1][11], y)
            if tile != -1:
                self.m.add_enter_event(Ee(y), (lambda yb: lambda: self.map_setup((mx+1,my), W(yb)))(tile))
                self.m.change_tile((10,y),'X')
        # Teleporting to left-top corner is not optimal when the hero is not
        # coming from the upper or left edge.
        # For non-edge entry we don't really know how should the hero be alligned,
        # but we can at least get edges done well.
        hero_x = (9 * 32 + 7) * tele_x / 9
        hero_y = (9 * 32 + 7) * tele_y / 9
        main_hero.teleport((hero_x, hero_y))
        if not keep_textbox:
            ui.change_text(to_a(map_title))
        # add_events last, as it may change text, tiles, or teleport hero once more
        add_events()
    def add_chara(self, chara_class, position = None, route = None, event = None):
        chara_obj = Chara(self.ui,self.m,chara_class,position=position,route=route)
        self.m.add_chara(chara_obj)
#        if route != None:
#            chara_obj.setup_route(route)
        if event != None:
            self.m.add_chara_event(chara_obj, event)
    #################################################################
    # Map setup routines
    # They only setup:
    # * charas
    # * objects: enemies, items, decorations
    # * events
    # * wormholes
    # * battle look
    # Other things (tiles, map passage, place names) are handled outside
    #################################################################
    #################################################################
    # Row 3
    def map_setup_0_3(self):
        pass

###########################################################
# This class does the worldmap UI                         #
###########################################################
class World_UI:
    def __init__(self, ui, w, main_hero):
        self.ui        = ui
        self.w         = w
        self.main_hero = main_hero
    def blit(self): # API changes
        ui.screen.fill((0,0,0),pygame.Rect((0,0),(640,320)))
        w.m.blit()
        ui.blit_text()
        mhc.blit_statistics()
        main_hero.blit()
    def main_loop(self):
        while 1:
            # Check UI events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    ui.key_down(event.key)
                    if event.key == pygame.K_RETURN:
                        pygame.display.toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE:
                        sys.exit()
                elif event.type == pygame.KEYUP:
                    ui.key_up(event.key)
            # Controller
            speed_sn = 0
            speed_ew = 0
            if ui.key_pressed(pygame.K_UP):
                speed_sn = speed_sn - 1
            if ui.key_pressed(pygame.K_DOWN):
                speed_sn = speed_sn + 1
            if ui.key_pressed(pygame.K_LEFT):
                speed_ew = speed_ew - 1
            if ui.key_pressed(pygame.K_RIGHT):
                speed_ew = speed_ew + 1
            main_hero.move(speed_ew*main_chara_speed, speed_sn*main_chara_speed)
            self.w.m.run_charas()
            self.blit()
            pygame.display.flip()
            ui.tick()

###########################################################
# Main                                                    #
###########################################################

ui   = UI()
w    = World(ui)
mhc  = Main_Hero_Controller()
main_hero = Chara(ui,w.m,"female-blue",position=(0,0))
main_hero.is_main = True # This isn't a particularly nice hack, subclass maybe ?
w.map_setup((0, 3), (4, 5))

world_ui = World_UI(ui,w,main_hero)
world_ui.main_loop()

