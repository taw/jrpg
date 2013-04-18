#!/usr/bin/python
# -*- coding: UTF-8 -*-
#############################################################
# THIS CODE IS COMMON TO BOTH BRANCHES                      #
#############################################################

import sys, pygame
from random import *
from math import *

###########################################################
# This class manages map tiles characteristics
###########################################################
# This class manages chara images
# De facto it's just useful, so that many chara of the same
# class can share image buffers.
class Chara_Tiles_Controller:
    def __init__(self, imgs):
        self.imgs = {}
        for k in imgs:
	    self.imgs[k] = pygame.image.load(imgs[k])
class Map_Tiles_Controller:
    def __init__(self, img, ttt, ett):
	self.ttt = {}
	for k in ttt:
	   (sx,sy,bs) = ttt[k]
	   self.ttt[k] = (pygame.Rect(sx*32,sy*32,32,32),bs)
	self.ett = {}
	for k in ett:
	   (sx,sy) = ett[k]
	   self.ett[k] = pygame.Rect(sx*32,sy*32,32,32)
	self.img = pygame.image.load(img)
    def blit(self, target, target_rect, tile_id):
	source_rect = self.ttt[tile_id][0]
	target.blit(self.img, target_rect, source_rect)
    def blit_enemy(self, target, target_rect, enemy_id):
	source_rect = self.ett[enemy_id]
	target.blit(self.img, target_rect, source_rect)
    def blocking(self, tile_id):
	return self.ttt[tile_id][1]
# anchor (0.0, 0.0) - loc is text's top left corner
# anchor (0.5, 0.5) - loc is text's center
# anchor (1.0, 1.0) - loc is text's bottom right corner
def render_text(target, font, text, loc, anchor, color):
    text_r = font.render(text, True, color)
    (x,y) = loc
    (w,h) = (text_r.get_width(), text_r.get_height())
    (ax,ay) = anchor
    fin_loc = (floor(x-ax*w),floor(y-ay*h))
    target.blit(text_r, fin_loc)

#############################################################
# Read the book of demons
class Book_of_demons:
    def __init__(self):
        f = open("demons.txt")
        lines = f.readlines()
        f.close()
        self.demons = {}
        for line in lines:
            fields = unicode(line, "UTF-8").strip(U"\n").split(U"\t")
            (demon_class,displayed_name) = (int(fields[0]), fields[1])
            secret_names = fields[2:len(fields)]
            if not self.demons.has_key(demon_class):
                self.demons[demon_class] = []
            self.demons[demon_class].append((displayed_name, secret_names))
    def random_from_class(self, demon_class):
        chapter = self.demons[demon_class]
        r = randint(0,len(chapter)-1)
        (dn, sns) = chapter[r]
        return ((demon_class,r), dn, sns)

#############################################################
# This class is needed merely for the statistics
class Main_Hero_Controller:
    def __init__(self):
        self.hpmax = 5
        self.hp    = self.hpmax
        self.xp    = 0
        self.xpfor = {}
        self.level = 0
    # One can only get XP for the same kind of demon N times
    # N=1 for quick debugging, N=3 or sth in the real game
    def xp_for_kill(self, demon):
        if not self.xpfor.has_key(demon):
            self.xpfor[demon] = 0
        if self.xpfor[demon] < 1:
            self.xpfor[demon] = self.xpfor[demon] + 1
            self.xp = self.xp + 1
    def hit(self, damage):
        self.hp = self.hp - damage
        if self.hp < 0:
            self.hp = 0
        # if self.hp == 0:
        #     we're dead, but it's up to the caller to take care of
    # This code works in battle mode and in worldmap mode
    def blit_statistics(self, target):
        target.blit(font.render("HP: %d/%d" % (self.hp, self.hpmax), 1, (0, 255, 0)), (336, 32+24))
        target.blit(font.render("XP: %d" % self.xp, 1, (0, 255, 0)), (336, 32))

ctc = Chara_Tiles_Controller({
    "female-blue" : "female-blue.png",
    "soldier-axe" : "soldier-axe.png",
    "soldier-elf" : "soldier-elf.png",
    "angel-blue"  : "angel-blue.png",
    "wizard-gray" : "wizard-gray.png",
    "man-worker"  : "man-worker.png",
    "elf-trader"  : "elf-trader.png",
    "arab-trader" : "arab-trader.png",
})
mtc = Map_Tiles_Controller("angband.png", {
# Movable terrain
  'g' : (  9, 23, False), # grass
  's' : ( 12, 23, False), # sand
  'h' : ( 93, 23, False), # hilly land
  'R' : ( 30, 23, False), # (stone) road
# Blocking terrain
  't' : ( 54, 23, True),  # tree
  'T' : ( 60, 23, True),  # pine tree
  'm' : (117, 23, True),  # mountain
  'r' : ( 96, 21, True),  # rocks
  '~' : ( 18, 23, True),  # water
  'P' : ( 69, 23, True),  # palm tree
  'C' : ( 99, 22, True),  # cactus
  'b' : ( 99, 24, True),  # brick wall
  'S' : (105, 24, True),  # stone wall
  'W' : (111, 24, True),  # wooden wall
  'B' : ( 78, 25, True),  # Blue brick wall
# Map edges
  'x' : (  0,  0, True),  # map border
  'X' : (  0,  0, False), # enter-able map border (must add event here)
  }, {
  "black rat" : (25, 13)
})

pygame.init()

book = Book_of_demons()

size   = (640, 480)
screen = pygame.display.set_mode(size, pygame.DOUBLEBUF)
font   = pygame.font.Font("/usr/share/fonts/truetype/kochi/kochi-gothic.ttf", 18)
clock  = pygame.time.Clock()


#############################################################
# THIS CODE IS *NOT* YET COMMON                             #
#############################################################

class Enemy_in_battle:
    def __init__(self, mtc, x, y, displayed_name, secret_names, xp_code, sprite_class):
	self.x              = x
	self.y              = y
	self.dx             = 0
	self.dy             = 0
	self.displayed_name = displayed_name
        self.secret_names   = secret_names
        self.active         = False
        self.xp_code        = xp_code
        self.mtc            = mtc
        self.sprite_class   = sprite_class
    def blit(self, target):
	global font
	(x0,y0) = (self.x+self.dx, self.y+self.dy)
	#target.blit(img_enemies, (x0,y0), (25*32, 13*32, 32, 32))
        mtc.blit_enemy(target, (x0,y0), self.sprite_class)
        if self.active:
            text_color = (255, 128, 160)
        else:
            text_color = (128, 64, 80)
        render_text(target, font, self.displayed_name, (x0+16,y0), (0.5, 1.0), text_color)
    def move(self):
        self.dx = self.dx + normalvariate(0,1)
        self.dy = self.dy + normalvariate(0,1)
        l = self.dx*self.dx + self.dy*self.dy 
        if l > 100:
	    l = sqrt(l)
	    self.dx = self.dx / l
	    self.dy = self.dy / l
    def activate(self):
        self.active = True
    def deactivate(self):
        self.active = False
    def secret_name_ok(self, secret_name):
        return secret_name in self.secret_names

# This class should manage killing enemies and activation/deactivation
class Enemies_in_battle:
    def __init__(self, mtc, book, chara):
        self.active  = -1
        self.enemies = []
        self.mtc     = mtc
        self.book    = book
        self.chara   = chara
    def add_enemy(self, sprite_class, demon_class):
        (xp_code, displayed_name, secret_names) = self.book.random_from_class(0)
        enemy = Enemy_in_battle(mtc, uniform(20, 120), uniform(20, 260), displayed_name, secret_names, xp_code, sprite_class)
        self.enemies.append(enemy)
    def attacked(self, attack_name):
        if self.active == -1: # No active enemies
            return # EXCEPTION
        if self.enemies[self.active].secret_name_ok(attack_name):
            self.chara.xp_for_kill(self.enemies[self.active].xp_code)
            self.kill_active()
        else:
            self.counter_attack()
            self.switch_active()
    def switch_active(self):
        if self.active != -1:
            self.enemies[self.active].deactivate()
        if len(self.enemies) > 0:
            self.active = randint(0, len(self.enemies)-1)
            self.enemies[self.active].activate()
        else:
            self.active = -1
    def kill_active(self):
        if self.active == -1:
            return
        self.enemies[self.active].deactivate()
        del self.enemies[self.active]
        self.active = -1
        self.switch_active()
    def counter_attack(self):
        self.chara.hit()
    def blit(self, target):
        for e in self.enemies:
            e.blit(target)
    def move(self):
        for e in self.enemies:
            e.move()

class Chara_in_battle:
    def __init__(self, (x, y), mhc, ctc):
	self.x     = x
	self.y     = y
        self.mhc   = mhc
        self.img   = ctc.imgs["female-blue"]
	self.buf   = U""
    def blit(self, target):
        target.blit(self.img, (self.x,self.y), (2*24, 3*32, 24, 32))
        render_text(target, font, self.buf, (self.x+12,self.y), (0.5, 1.0), (64, 128, 255))
    def attack(self,enemies):
        if self.buf == U"":
            return
        enemies.attacked(self.buf)
        self.buf = U""
    def hit(self):
        self.mhc.hit(1)
        if self.mhc.hp == 0:
            pass # EXCEPTION
    def xp_for_kill(self, demon):
        self.mhc.xp_for_kill(demon)

class Battle_UI:
    def __init__(self, book, mhc, mtc, ctc):
       self.chara   = Chara_in_battle((240,160),mhc,ctc)
       self.enemies = Enemies_in_battle(mtc,book,self.chara)
    # Call switch_active() every time we add a new enemy instead of
    # having explicit ok_thats_all_enemies() call.
    # It simplifies the API and the result is the same.
    def add_enemies(self, count, sprite_class, demon_class):
        for i in range(count):
            self.enemies.add_enemy(sprite_class, demon_class)
        self.enemies.switch_active()
    def blit(self, target):
        global font
        target.fill((0,0,0))
        target.fill((0,128,0), (0,0,320,320))
        self.chara.blit(screen)
        self.enemies.blit(screen)
        self.chara.mhc.blit_statistics(screen)
    def main_loop(self):
        global screen
        global clock
        while 1:
            # Check UI events
            for event in pygame.event.get():
	       if event.type == pygame.QUIT:
	           sys.exit()
	       elif event.type == pygame.KEYDOWN:
	           if event.key == pygame.K_RETURN:
	               pygame.display.toggle_fullscreen()
	           elif event.key == pygame.K_ESCAPE:
	               sys.exit()
                   elif event.key >= 97 and event.key <= 122: #'a'..'z'
                       self.chara.buf = self.chara.buf + chr(event.key)
                   elif event.key == 32: # space
                       self.chara.attack(self.enemies)
            self.enemies.move()
            self.blit(screen)
            pygame.display.flip()
            clock.tick(100)

mhc = Main_Hero_Controller()

battle = Battle_UI(book, mhc, mtc, ctc)
battle.add_enemies(5, "black rat", 0)

battle.main_loop()
