#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pygame, sys, pickle
from random import *

# Import other jrpg modules
import resman
import demonsoul
from spatial_index import Index
import util
from util import sgn, Cached, Notifier

util.init_pygame("JRPG 2 demo")

# Debug controls
ignore_walls = False

###########################################################
# A few helpful functions                                 #
###########################################################
def sgn2((to_x,to_y),(from_x,from_y)):
    return (sgn(to_x-from_x), sgn(to_y-from_y))
def clamp(x, x_min, x_max):
    if x < x_min:
        return x_min
    elif x > x_max:
        return x_max
    else:
        return x

###########################################################
# Base class for NPCCtl, MainCharaCtl and EnemyCtl        #
###########################################################
class CharaCtl:
    vec2diri = {
        (-1,-1) : 7,
        ( 0,-1) : 0,
        ( 1,-1) : 1,
        (-1, 0) : 6,
        ( 1, 0) : 2,
        (-1, 1) : 5,
        ( 0, 1) : 4,
        ( 1, 1) : 3,
        ( 0, 0) : 4, # Just to avoid crashes
    }
    diri2vec = [
        ( 0,-1),
        ( 1,-1),
        ( 1, 0),
        ( 1, 1),
        ( 0, 1),
        (-1, 1),
        (-1, 0),
        (-1,-1),
    ]
    def __init__(self, sprite, initial_action, pos=None, respawn_func=None):
        self.sprite = sprite
        self.dir = 4
        self.respawn_func = respawn_func

        self.action = initial_action
        self.aniframe = 0
        self.anirepeat = True

        self.delay = 0
        self.delayed_event = None
        
        if pos:
            (self.x, self.y) = pos
        elif respawn_func:
            self.respawn(True)
        else:
            raise "Cannot initialize chara: neither position nor respawn function given"

        # A bit silly
        self.route = None
    def set_delayed_event(self, delay, delayed_event):
        self.delay = delay
        self.delayed_event = delayed_event
    def set_action(self, action, anirepeat=True):
        if action != self.action:
            self.action = action
            self.aniframe = 0
            self.anirepeat = anirepeat
    def set_dir(self, (dir_x, dir_y)):
        # Just a safety precaution, it should already be sgn2-ed
        (dir_x, dir_y) = (sgn(dir_x), sgn(dir_y))
        self.dir = CharaCtl.vec2diri[(dir_x, dir_y)]
    def get_dir(self):
        return CharaCtl.diri2vec[self.dir]
    def get_pos(self):
        return (self.x, self.y)
    def get_bb(self):
        return pygame.Rect((self.x-24, self.y-24), (48, 48))
    def render(self, target, (ofs_x, ofs_y)):
        resman.imgctl.render_sprite(target, self.sprite, self.action, self.dir, self.aniframe, (self.x-ofs_x, self.y-ofs_y))
        self.aniframe += 1
        # FIXME: abstraction broken here
        if self.aniframe == 2*resman.imgctl.frame_count(self.sprite, self.action):
            if self.anirepeat:
                self.aniframe  = 0
            else:
                self.aniframe -= 1
    # Ugly API
    # Returns whether it succeded
    # Assumes a single can_enter method for all (no fliers, swimmers etc)
    def move_low_level(self, (dir_x, dir_y)):
        (new_x,new_y) = (self.x+dir_x, self.y+dir_y)
        new_bb = pygame.Rect((new_x-24, new_y-24), (48, 48))
        if world.can_enter(new_bb):
            self.x += dir_x
            self.y += dir_y
            return True
        else:
            return False
    def setup_route(self, route):
        self.route = route
        self.route_i = 0
    # return False if cannot move in that direction
    def move_to(self, target):
        dir = sgn2(target, self.get_pos())
        if dir == (0,0):
            return False
        self.dir = CharaCtl.vec2diri[dir]
        return self.move_low_level(dir)
    def move_around(self, speed):
        #print "Moving around <%s> -> <%s>", self.get_pos(), self.route[self.route_i]
        if not self.route:
            return
        for i in range(speed):
            if not self.move_to(self.route[self.route_i]):
                self.route_i = (self.route_i+1) % len(self.route)
    # The default action is to just go if the character has a route
    # or stand in place if it doesn't
    def perform_actions(self):
        if self.perform_delayed():
            return
        self.move_around(4)
    def perform_delayed(self):
        if self.delay:
            #print "Delay", self.delay, ", action", self.delayed_event
            self.delay -= 1
            # delay is over, fire the event
            if not self.delay:
                # self.delayed_event() may reinstall self.delayed_event
                # So first clear, then run
                ev = self.delayed_event
                self.delayed_event = None
                ev()
            return True
        else:
            return False
    def respawn(self, force=False):
        while True:
            (x, y) = self.respawn_func()
            # Found the right place
            if world.can_enter(pygame.Rect((x-24, y-24), (48, 48))):
                (self.x, self.y) = (x, y)
                # Some chara (like Freya) have "running" as a default action
                self.set_action("walking")
                return
            # Didn't find the right place
            if force:
                # Try again (at initial respawn)
                continue
            else:
                # Delay (at later respawns)
                self.set_delayed_event(10, lambda: self.respawn())
                return

# Doctor is either healing or walking around
# (no standing doctors out there)
class DocCtl(CharaCtl):
    def __init__(self, pos):
        CharaCtl.__init__(self, "doc", "walking", pos=pos)
        self.healing = 0
    # It directly accesses mcc.hp and mcc.hpmax, ugly
    def perform_actions(self):
        if self.healing:
            self.healing -= 1
            # Main character walked away :-)
            if not self.get_bb().colliderect(mcc.get_bb()):
                self.healing = 0
                self.set_action("walking")
            # Healing finished
            elif self.healing == 0:
                # well, get_hpmax() wouldn't violate the astraction as much
                world.stats.set_hp(world.stats.hpmax)
                self.set_action("walking")
        else:
            if self.get_bb().colliderect(mcc.get_bb()) and world.stats.hp != world.stats.hpmax:
                self.healing = 30
                self.dir = CharaCtl.vec2diri[sgn2(mcc.get_pos(), self.get_pos())]
                self.set_action("healing")
            else:
                self.move_around(3)

# Enemies move around
class EnemyCtl(CharaCtl):
    def __init__(self, sprite, respawn_func):
        CharaCtl.__init__(self, sprite, "walking", respawn_func=respawn_func)
        self.select_random_direction()
        # Different enemies = different speeds
        self.speed = 2
        self.been_hit = 0
    def select_random_direction(self):
        self.dir = randint(0,7)
    def hit(self):
        self.set_delayed_event(22, lambda: self.set_action("attack"))
        self.set_action("tipping over")
    def perform_actions(self):
        if self.perform_delayed():
            return
        # No other actions in battle mode
        if world.in_battle_mode:
            return
        for i in range(self.speed):
            # Can smell the player ?
            # Then, turn to that direction
            smell_range = 256
            smell_bb = pygame.Rect((self.x - smell_range, self.y - smell_range), (2*smell_range, 2*smell_range))
            mc_bb = mcc.get_bb()
            if smell_bb.colliderect(mc_bb):
                self.dir = CharaCtl.vec2diri[sgn2(mcc.get_pos(), self.get_pos())]
            if random() < 0.01:
                self.select_random_direction()
            # Can move in the current direction ?
            # If not, change the direction, even if
            # we smell the player
            if not self.move_low_level(CharaCtl.diri2vec[self.dir]):
                self.select_random_direction()
            # Got to the player ? Start a fight
            if self.get_bb().colliderect(mc_bb):
                # The smelling thing should alruady turn us
                # in the right direction
                self.dir = CharaCtl.vec2diri[sgn2(mcc.get_pos(), self.get_pos())]
                world.enter_battle_mode(self)

###########################################################
# Controller for the main character                       #
###########################################################
class MainCharaCtl(CharaCtl):
    def __init__(self):
        # Is it ugly or what ?
        CharaCtl.__init__(self, "freya", "looking", pos=(122*16, 79*16))
    def hit(self):
        self.set_delayed_event(22, lambda: self.set_action("attack"))
        self.set_action("tipping over")
    def perform_actions(self):
        if self.perform_delayed():
            return
        # No other actions in battle mode
        if world.in_battle_mode:
            return
        (attacking, dir_x, dir_y) = self.ctl
        speed = 8
        if dir_x != 0 or dir_y != 0:
            self.dir = CharaCtl.vec2diri[(dir_x, dir_y)]
            if not attacking: self.set_action("running") # "walking"
            for i in range(speed):
                if not self.move_low_level((dir_x, dir_y)):
                    break
        elif not attacking: self.set_action("looking")
        if attacking: self.set_action("attack")
        world.update_ofs(mcc.get_pos())
    # An alternative would be keeping this in UI
    # and calling ui.get_mc_ctl()
    def set_ctl(self, ctl_state):
        self.ctl = ctl_state # (attacking, dir_x, dir_y)

###########################################################
# This class manages main chara statistics                #
# This is supposed to be part of the model (World)        #
###########################################################
class Statistics:
    def __init__(self):
        self.name  = u"Freya"
        self.xp    = 0
        self.level = 0
        self.hp    = 5
        self.hpmax = 5
        self.money = 0
        self.xpctl = demonsoul.XpCtl()
        
        self.nctl_stats_changed = Notifier()
    def set_hp(self, new_hp):
        self.hp = new_hp
        # TODO: being-dead handler
        self.nctl_stats_changed.fire()
    def damage(self, amount):
        new_hp = max(self.hp - amount, 0)
        self.set_hp(new_hp)
    def get_xp(self, xp_gain):
        self.xp += xp_gain
      
        new_level = self.level+1
        next_level_xp_req = new_level * (95 + new_level * 5)
        while self.xp >= next_level_xp_req :
            self.level = self.level + 1
            self.hpmax = self.hpmax + 1
            self.hp    = self.hp + 1

            new_level  = self.level+1
            next_level_xp_req = new_level * (95 + new_level * 5)
        world.msg_add(["%s advanced to level %d" % (self.name, self.level)])
        self.nctl_stats_changed.fire()
    def beat(self, soul):
        if self.xpctl.see_or_beat_soul(soul):
            self.get_xp(soul.xp_for_win())
            self.nctl_stats_changed.fire()

# State-of-the-world manager
# This is the "model" of the world
# All queries about the state of the world
# should go through this class
#
# For cleanliness, it should not do any UI
# It pretty much sucks that cache controller
# doesn't let us separate it cleanly.
class World:
    def __init__(self, map_id):
        self.ofs_x  = 122*16
        self.ofs_y  = 79*16
        self.msg    = [u"Welcome to JRPG 2 demo", u"夢もなければ生きられない。", u"Man can't live without dreams."]
        self.map_id = map_id
        
        self.stats = Statistics()
        
        self.in_battle_mode = False

        self.nctl_msg_changed = Notifier()
        self.nctl_bg_changed  = Notifier()

        self.reload_map()

        doc = DocCtl((120*16, 60*16))
        doc.setup_route([(125*16, 75*16), (120*16, 60*16)])
        self.npcs = [doc]
        
        def respawn_in_forest():
            while True:
                x = randint(3*16,(40*4-4)*16)
                y = randint(3*16,(40*3-4)*16)
                # Not in the village
                if x > 23*64 and y > 16*48:
                    continue
                break
            return (x,y)

        def respawn_in_desert():
            x = randint(3*16,(40*4-4)*16)
            y = randint(42*48,68*48)
            return (x,y)
        
        # FIXME: really really ugly hack
        # EnemyCtl() requires world global object, but we're just
        # trying to build it
        global world
        world = self
        
        # Dispatch a few enemies in the forest
        for i in range(5):
           enemy = EnemyCtl("red_spider", respawn_in_forest) 
           self.npcs.append(enemy)

        # And a few in the desert
        for i in range(5):
           enemy = EnemyCtl("red_spider", respawn_in_desert) 
           self.npcs.append(enemy)
    def msg_add(self, msg):
        self.msg = msg + self.msg
        # TODO: Cut if too long
        self.nctl_msg_changed.fire()
    def reload_map(self):
        (sz_x, sz_y, tiles, objs) = resman.mapdb.get_map_data(self.map_id)
        self.current_map = resman.CurrentMap((sz_x,sz_y), tiles)
        self.map_objects = objs
        self.sz_x = sz_x
        self.sz_y = sz_y

        self.obstacle_idx = Index()
        self.posval_idx   = Index()
        for (obj_id, pos_x, pos_y) in self.map_objects:
            (hsz_x, hsz_y, val) = resman.object_properties.get(obj_id,(0,0,0))
            if val == 1:
                obj_bb = pygame.Rect((16*pos_x-hsz_x,16*pos_y-hsz_y), (2*hsz_x,2*hsz_y))
                self.posval_idx.add(obj_bb, True)
            elif val == -1:
                obj_bb = pygame.Rect((16*pos_x-hsz_x,16*pos_y-hsz_y), (2*hsz_x,2*hsz_y))
                self.obstacle_idx.add(obj_bb, True)
        self.nctl_bg_changed.fire()
    # (pos_x, pos_y) is the chara's *center*, in pixels,
    # from the map's upper left corner
    #
    # Smooth scrolling looks cooler, but screws the cache :-(
    # If it's really necessary for gameplay, we can render
    # a bigger map (like, with 128px margins around)
    # to keep the bg cache valid longer
    def update_ofs(self, (pos_x, pos_y)):
        # 12x12 is viewport size
        (ofs_x, ofs_y) = (self.ofs_x, self.ofs_y)

        viewport_pos_x = pos_x - ofs_x
        while viewport_pos_x < 64*3 and ofs_x > 0:
            ofs_x = max(ofs_x-128, 0)
            viewport_pos_x = pos_x - ofs_x
        while viewport_pos_x > 786-64*3 and ofs_x < 64*(self.sz_x - 12):
            ofs_x = min(ofs_x+128, 64*(self.sz_x-12))
            viewport_pos_x = pos_x - ofs_x

        viewport_pos_y = pos_y - ofs_y
        while viewport_pos_y < 48*3 and ofs_y > 0:
            ofs_y = max(ofs_y-128,0)
            viewport_pos_y = pos_y - ofs_y
        while viewport_pos_y > 576-48*3 and ofs_y < 48*(self.sz_y - 12):
            ofs_y = min(ofs_y+128,48*(self.sz_y - 12))
            viewport_pos_y = pos_y - ofs_y

        if ofs_x != self.ofs_x or ofs_y != self.ofs_y:
            self.nctl_bg_changed.fire()
            self.ofs_x = ofs_x
            self.ofs_y = ofs_y
    def update_ofs_center(self):
        (mc_x, mc_y) = mcc.get_pos()
        ofs_x = clamp(mc_x - 32*12, 0, 64*(self.sz_x - 12))
        ofs_y = clamp(mc_y - 24*12, 0, 48*(self.sz_y - 12))
        
        if ofs_x != self.ofs_x or ofs_y != self.ofs_y:
            self.nctl_bg_changed.fire()
            self.ofs_x = ofs_x
            self.ofs_y = ofs_y
    def get_ofs(self):
        return (self.ofs_x, self.ofs_y)
    def can_enter(self, bb):
        # For debug mode
        if ignore_walls:
            return True
        bg_colisions = self.current_map.obstacle_idx.intersect_rect(bb)
        for (c_bb,c_e) in bg_colisions:
            if not self.posval_idx.contains_rect_p(c_bb):
                #print "Collides", c_bb
                return False
            #else:
            #    print "Bypassed", c_bb
        # All collisions with the backgrounds have been bypassed by bridges
        # (or there haven't been any in the first place)
        
        return not self.obstacle_idx.intersects_rect_p(bb)
    def get_map_objects(self):
        return self.map_objects
    def perform_actions(self):
        if self.in_battle_mode:
            mcc.perform_actions()
            self.enemy.perform_actions()
            # Every one else is idle during battle
        else:
            mcc.perform_actions()
            for npc in self.npcs:
                npc.perform_actions()
    def enter_battle_mode(self, enemy):
        self.in_battle_mode = True
        self.update_ofs_center()
        self.enemy = enemy
        mcc.set_dir(sgn2(enemy.get_pos(), mcc.get_pos()))
        
        enemy.set_action("attack")
        mcc.set_action("attack")
        
        self.enemy_class = [(3, 500)]
        self.enemy_soul  = book.get_one(self.stats.xpctl, self.enemy_class)
        self.enemy_hp    = 5
    def leave_battle_mode(self):
        self.in_battle_mode = False
    def attack(self, attack_text):
        if self.enemy_soul.answer_ok(attack_text):
            self.enemy_hp -= 1
            if self.enemy_hp == 0:
                self.enemy.set_action("tipping over", False)
                # How long should it stay there ?
                # 15s [=600 frames, hopefully] ?
                # Early binding, self.enemy may be something else
                # when it fires
                e = self.enemy
                self.enemy.set_delayed_event(600, lambda: e.respawn())
                self.in_battle_mode = False
            else:
                self.enemy.hit()
                self.stats.beat(self.enemy_soul)
                self.enemy_soul = book.get_one(self.stats.xpctl, self.enemy_class)
        else:
            mcc.hit()
            self.stats.damage(1)
            hints = self.enemy_soul.get_hints()
            if hints:
                self.msg_add(hints)
            self.enemy_soul = book.get_one(self.stats.xpctl, self.enemy_class)
# Some minimal versions of save and load
# It's called savefile.dat not savefile, to avoid conflict with jrpg 1
# No protection yet
    def save(self):
        save_data = {
            "name"     : self.stats.name,
            "hpmax"    : self.stats.hpmax,
            "hp"       : self.stats.hp,
            "xp"       : self.stats.xp,
            "level"    : self.stats.level,
            "money"    : self.stats.money,
            "xpfor"    : self.stats.xpctl.dump(),
        }
        f = open("savefile.dat", "w")
        pickle.dump(save_data, f)
        f.close()
        self.msg_add([u"Game saved"])
    def load(self):
        f = open("savefile.dat", "r")
        ld = pickle.load(f)
        self.stats.name      = ld.get("name", "Freya")
        self.stats.hpmax     = ld["hpmax"]
        self.stats.hp        = ld["hp"]
        self.stats.xp        = ld["xp"]
        self.stats.level     = ld["level"]
        self.stats.money     = ld["money"]
        self.stats.xpctl     = demonsoul.XpCtl(ld["xpfor"])
        self.stats.nctl_stats_changed.fire()
        self.msg_add([u"Game loaded"])

class UI:
    def __init__(self):
        size = (width, height) = (1024, 768)
        pygame.display.set_icon(pygame.image.load("images/jrpg-icon.png"))
        self.screen = pygame.display.set_mode(size, pygame.DOUBLEBUF) # |pygame.HWSURFACE
        self.key_pressed_table = [False for i in range(512)]
        self.clock = pygame.time.Clock()
        self.frame_number = 0
        self.map_viewport     = self.screen.subsurface(((32,32),(768,576)))
        self.stats_viewport   = self.screen.subsurface(((768+2*32,32),(1024-768-3*32,576)))
        self.msg_viewport     = self.screen.subsurface(((32,576+2*32),(768,768-576-3*32)))

        self.bg_cache_surface = pygame.Surface((768, 576))
        self.bg_cache         = Cached(lambda: self.refresh_bg_cache(), world.nctl_bg_changed)
        self.stats_cache      = Cached(lambda: self.render_stats(self.stats_viewport), world.stats.nctl_stats_changed)
        self.msg_cache        = Cached(lambda: self.render_msg(), world.nctl_msg_changed)
        # FIXME: The last small square is pretty much unused
        # It will probably be a good idea to take half of stat viewport and
        # that square to make a demon viewport or sth

        self.default_font, self.furi_font, self.big_font = util.load_font(18, 24, 64)

        self.buf       = u""
        self.bs_repeat = 0
        
        # This is just UI state
        self.in_battle_mode = False
    def key_down(self, key):
        self.key_pressed_table[key] = True
    def key_up(self, key):
        self.key_pressed_table[key] = False
    def key_pressed(self, key):
        return self.key_pressed_table[key]
    def tick(self):
        fpsLimit = 40
        self.frame_number += 1
        if 0: # Low-CPU version
            time_so_far = self.clock.tick()
            time_max    = int(1000.0/fpsLimit)
            time_left   = time_max - time_so_far
            if time_left > 0:
                pygame.time.wait(time_left)
            #print time_left, self.clock.get_fps()
        else: # Version for exact measurement - do not use :-)
            self.clock.tick()
            #print self.clock.get_fps()
    def render_msg(self):
        self.msg_viewport.fill((0,0,0))
        msg_text_color = (0xC0, 0xE0, 0xFF)
        line_height = 24
        for i in range(len(world.msg)):
            t = self.default_font.render(world.msg[i], True, msg_text_color)
            self.msg_viewport.blit(t, (0, i * line_height))
    def world_mode_loop_iter(self):
        global ignore_walls

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self.key_down(event.key)
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                if event.key == pygame.K_RETURN:
                    pygame.display.toggle_fullscreen()
                if event.key == pygame.K_F2:
                    world.save()
                if event.key == pygame.K_F4:
                    world.load()
                if event.key == ord('r'):
                    reload(resman)
                    world.reload_map()
                if event.key == ord('i'):
                    ignore_walls = not ignore_walls
                    world.msg_add([u"Ignore walls set to " + str(ignore_walls)])
                if event.key == ord('l'):
                    (x,y) = mcc.get_pos()
                    x = int(round(x/16.0))
                    y = int(round(y/16.0))
                    world.msg_add([u"Current position: <%d, %d>" % (x,y)])
            elif event.type == pygame.KEYUP:
                self.key_up(event.key)
        dir_x = 0
        dir_y = 0
        attacking = 0
        if self.key_pressed(pygame.K_UP):
            dir_y -= 1
        if self.key_pressed(pygame.K_DOWN):
            dir_y += 1
        if self.key_pressed(pygame.K_LEFT):
            dir_x -= 1
        if self.key_pressed(pygame.K_RIGHT):
            dir_x += 1
        if self.key_pressed(pygame.K_SPACE):
            attacking = 1
        mcc.set_ctl((attacking, dir_x, dir_y))

        # Now move, render, flip and tick
        world.perform_actions()
        self.render()
        pygame.display.flip()
        self.tick()
    def battle_mode_loop_iter(self):
        # TODO: well, make it actually work
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self.key_down(event.key)
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                elif event.key >= 97 and event.key <= 122: #'a'..'z'
                    self.buf = self.buf + chr(event.key)
                elif event.key == 32: # space
                    world.attack(self.buf)
                    self.buf = u""
                # TODO: here
            elif event.type == pygame.KEYUP:
                self.key_up(event.key)
        if self.key_pressed(pygame.K_BACKSPACE):
            if self.bs_repeat == -1: # Fresh
                self.buf = self.buf[0:len(self.buf)-1]
                self.bs_repeat = 5
            if self.bs_repeat == 0:
                self.buf = self.buf[0:len(self.buf)-1]
                self.bs_repeat = 2
            else:
                self.bs_repeat = self.bs_repeat - 1
        # Now move, render, flip and tick
        world.perform_actions()
        self.render()
        pygame.display.flip()
        self.tick()       
    def main_loop(self):
        while 1:
            if world.in_battle_mode and not self.in_battle_mode:
                self.buf = u""
                self.bs_repeat = 0
                self.in_battle_mode = world.in_battle_mode
            if world.in_battle_mode:
                self.battle_mode_loop_iter()
            else:
                self.world_mode_loop_iter()
    # FIXME: The unlikely case that mc and enemy are on the same tile
    # and facing the same direction is not handled here
    # FIXME: for names longer than 4, it may get out of screen
    def render_kanji_name(self, (rel_x, rel_y), (anchor_x,anchor_y)):
        furicode   = world.enemy_soul.furicode()
        font_main  = self.big_font
        font_furi  = self.furi_font
        color_base = (212, 228, 255)
        # FIXME: find a nice color
        color_furi = (  0,   0,  64)

        displayed_elements = []
        
        (x,miny,maxy) = (0,0,0)
        
        for (base, furi, keep_furi) in furicode:
            base_rendered = font_main.render(base, True, color_base)
            (w, h) = (base_rendered.get_width(), base_rendered.get_height())
            displayed_elements.append((x,0,base_rendered))
            #if furi and (keep_furi or display_all_furi):
            # FIXME: don't display furi always
            maxy = max(maxy, h)
            if furi and (keep_furi or not world.stats.xpctl.seen_soul(world.enemy_soul)):
                if keep_furi:
                    furi_rendered = font_furi.render(furi, True, color_base)
                else:
                    furi_rendered = font_furi.render(furi, True, color_furi)
                (fw,fh) = (furi_rendered.get_width(), furi_rendered.get_height())
                displayed_elements.append((x-fw/2+w/2, -fh, furi_rendered))
                miny = min(miny, -fh)
            x = x + w
        # Now, displayed_elements is a box (0,-miny)..(x, maxy)

        # Compute distance from to the upper left corner to the anchor
        # (anchor is in the middle of the kanji, ignoring furi)
        # TODO: is it better than including furi ?
        (cx, cy) = (-x/2, -maxy/2)
        # If anchor is (-1,-1), display at the anchor
        # If anchor is (0, 0) shift by (cx,cy)
        # If anchor is (1,1), shift by (2 cx,2 cy)
        # etc.
        (dx, dy) = ((anchor_x+1)*cx, (anchor_y+1)*cy)

        #print (cx, cy, anchor_x, anchor_y, (x, miny, maxy))
        for (x, y, displayed_element) in displayed_elements:
            #print (rel_x, x, dx, rel_y, y, dy)
            self.map_viewport.blit(displayed_element, (rel_x+x+dx, rel_y+y+dy))
    def render_chara_attack(self, chara_attack, (x,y)):
        chara_attack_color = (228, 228, 255)
        chara_attack_rendered = self.big_font.render(chara_attack, True, chara_attack_color)
        self.map_viewport.blit(chara_attack_rendered, (x-chara_attack_rendered.get_width()/2, y-chara_attack_rendered.get_height()/2))
    def render(self):
        self.render_map()
        mcc.render(self.map_viewport, world.get_ofs())
        for npc in world.npcs:
            npc.render(self.map_viewport, world.get_ofs())
        if world.in_battle_mode:
            # FIXME: It's completely wrong if the battle takes place
            # on the map edge
            (ofs_x, ofs_y) = world.get_ofs()

            (e_x, e_y) = world.enemy.get_pos()
            (e_dir_x, e_dir_y) = world.enemy.get_dir()
            #(x, y) = (e_x - ofs_x - e_dir_x * 64, e_y - ofs_y - e_dir_y * 64)
            (x, y) = (e_x - ofs_x - e_dir_x * 64, e_y - ofs_y - e_dir_y * 64)
            self.render_kanji_name((x, y), (e_dir_x, e_dir_y))

            (mc_x, mc_y) = mcc.get_pos()
            (mc_dir_x, mc_dir_y) = mcc.get_dir()
            (x, y) = (mc_x - ofs_x - mc_dir_x * 64, mc_y - ofs_y - mc_dir_y * 64)
            self.render_chara_attack(self.buf, (x, y))
        self.stats_cache.execute()
        self.msg_cache.execute()
    def render_map(self):
        self.bg_cache.execute()
        # Actually we could limit ourselves to just blitting the
        # affected parts (one around the current character)
        # Too easy to get it wrong thou
        self.map_viewport.blit(self.bg_cache_surface, (0,0))
    def refresh_bg_cache(self):
        self.bg_cache_surface.fill((0,0,0))
        ofs = world.get_ofs()
        world.current_map.render(self.bg_cache_surface, ofs)
        # FIXME:render items top to bottom
        for (obj_type, x, y) in world.get_map_objects():
            resman.imgctl.render_map_obj(self.bg_cache_surface, obj_type, (x,y), ofs)
    def render_stats(self, target):
        target.fill((0,0,0))
        stats_text_color = (0xC0, 0xE0, 0xFF)
        line_height = 24

        stats = world.stats

        txt = [
            stats.name,
            "Level: %s" % stats.level,
            "XP: %s" % stats.xp,
            "HP: %s/%s" % (stats.hp, stats.hpmax),
            "Money: %s euro" % stats.money,
        ]
        for i in range(len(txt)):
            t = self.default_font.render(txt[i], True, stats_text_color)
            target.blit(t, (0, i * line_height))

try:
    # The only reason we initialize it here is
    # because it's slow and we want to minimize the time
    # between graphic mode switch and actually displaying something
    book = demonsoul.Book_of_demons()
    
    # FIXME: There are too many cyclic dependencies between the 3
    world = World("main")
    mcc = MainCharaCtl()
    ui = UI()
    ui.main_loop()
except Exception:
    util.save_errormsg(sys.exc_info())
    raise
