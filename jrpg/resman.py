#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Resource manager for JRPG 2

import pygame
from random import *

# Import other jrpg modules
from spatial_index import Index

###########################################################
# Aux functions                                           #
###########################################################
#
# sort() can do something like that but only in 2.4
# We need to do Schwartzian Transform for 2.3-compatibility
#
# It's a functional sort.
# (Python's #sort being really #sort! is so ugly)
def sortby(a_list, key_func):
    new_list = [(key_func(val), val) for val in a_list]
    new_list.sort()
    return [val for (key, val) in new_list]

###########################################################
# Img controller                                          #
###########################################################

class SpriteImages:
    directions = ["n", "ne", "e", "se", "s", "sw", "w", "nw"]
    def __init__(self, directory):
        self.directory = directory
        # Action => Direction => FrameIndex => Image
        self.img = {}
    def load(self, action):
        self.img[action] = [[] for d in range(8)]
        for d in range(8):
            i = 0
            try:
                while True:
                    fn = "images/%s/%s %s%04d.png" % (self.directory, action, SpriteImages.directions[d], i)
                    img = pygame.image.load(fn)
                    self.img[action][d].append(img)
                    i += 1
            except Exception:
                if len(self.img[action][d]) == 0:
                    raise Exception("No images for %s.%s in %s" % (action, SpriteImages.directions[d], self.directory))
    # <ofs_x, ofs_y> in pixels, not 16-blocks
    # We specify *Center*, not upper left corner here
    def render(self, target, action, direction, ofs_t, (ofs_x, ofs_y)):
        imgs = self.img[action][direction]
        # Animation frame every 2 display frames
        img = imgs[(ofs_t/2) % len(imgs)]
        x = ofs_x-img.get_width()/2
        y = ofs_y-img.get_height()/2
        target.blit(img,(x,y))

class ImgCtl:
    def __init__(self, sprites_def, tilesets_def, tiles_def):
        self.chara = {}
        for key in sprites_def:
            (file_name, actions) = sprites_def[key]
            self.chara[key] = SpriteImages(file_name)
            for action in actions:
                self.chara[key].load(action)
        self.tilesets = {}
        # Load the resources
        for key in tilesets_def:
            self.tilesets[key] = pygame.image.load(tilesets_def[key]) # .convert_alpha()
        self.tiles = {}
        for key in tiles_def:
            (file_id, x, y, sz_x, sz_y) = tiles_def[key]
            self.tiles[key] = self.tilesets[file_id].subsurface((16*x, 16*y), (16*sz_x, 16*sz_y))
    # <ofs_x, ofs_y> in pixels, not 16-blocks
    # We specify *Center*, not upper left corner here
    def render_sprite(self, target, sprite_id, action, direction, ofs_t, (ofs_x, ofs_y)):
        self.chara[sprite_id].render(target, action, direction, ofs_t, (ofs_x, ofs_y))
    def render_map_tile(self, target, tile_id, (ofs_x, ofs_y)):
        target.blit(self.tiles[tile_id], (ofs_x, ofs_y))
    def render_map_obj(self, target, tile_id, (ofs_x, ofs_y), (view_ofs_x, view_ofs_y)):
        (x,y) = (16*ofs_x-view_ofs_x, 16*ofs_y-view_ofs_y)
        img = self.tiles[tile_id]
        target.blit(img, (x-img.get_width()/2,y-img.get_height()/2))
    # For coast computations
    def tile_exists(self, tile_id):
        return self.tiles.has_key(tile_id)
    # We assume the count is the same in all directions
    def frame_count(self, sprite_id, action):
        return len(self.chara[sprite_id].img[action][0])

###########################################################
# Map                                                     #
###########################################################

# Extra function definition
# It's totally silly, but python doesn't let us do (b ? "+" : "-")
def bool_sym(b):
    if b:
        return "+"
    else:
        return "-"

# This is an ugly class
# The only thing it really does is precomputing the map
# It should probably be moved to World
class CurrentMap:
    def __init__(self, (sz_x, sz_y), map_data):
        # Raw data
        self.map_data = map_data
        self.sz_x = sz_x
        self.sz_y = sz_y
        # Tile ids
        self.map_tiles = [[None for x in range(sz_x)] for y in range(sz_y)]

        # In half-tiles
        # Get rid of and replace by an obstacle idx
        #self.map_can_enter = [[True for x in range(2*sz_x)] for y in range(2*sz_y)]

        # This is a little hopeless, as the old structure
        # worked much faster ;-)
        self.obstacle_idx = Index()

        for y in range(sz_y):
            for x in range(sz_x):
                if self.map_data[y][x] == ' ':
                    self.map_tiles[y][x] = "grass"
                elif self.map_data[y][x] == 'w':
                    ctx = self.map_ctx4(x,y,'w')
                    #self.map_can_enter[2*y  ][2*x  ] = ctx[0]
                    #self.map_can_enter[2*y  ][2*x+1] = ctx[1]
                    #self.map_can_enter[2*y+1][2*x  ] = ctx[2]
                    #self.map_can_enter[2*y+1][2*x+1] = ctx[3]

                    if not ctx[0]: self.obstacle_idx.add(pygame.Rect((64*x,    48*y),   (32,24)), True)
                    if not ctx[1]: self.obstacle_idx.add(pygame.Rect((64*x+32, 48*y),   (32,24)), True)
                    if not ctx[2]: self.obstacle_idx.add(pygame.Rect((64*x,    48*y+24),(32,24)), True)
                    if not ctx[3]: self.obstacle_idx.add(pygame.Rect((64*x+32, 48*y+24),(32,24)), True)

                    code = "w|%s%s%s%s" % (bool_sym(ctx[0]), bool_sym(ctx[1]), bool_sym(ctx[2]), bool_sym(ctx[3]))
                    if imgctl.tile_exists(code):
                        self.map_tiles[y][x] = code
                    else:
                        # No special tile -> better ugly than segfault
                        self.map_tiles[y][x] = "water"
                elif self.map_data[y][x] == 'r':
                    ctx = self.map_ctx4(x,y,'r')
                    code = "r|%s%s%s%s" % (bool_sym(ctx[0]), bool_sym(ctx[1]), bool_sym(ctx[2]), bool_sym(ctx[3]))
                    if imgctl.tile_exists(code):
                        self.map_tiles[y][x] = code
                    else:
                        # No special tile -> better ugly than segfault
                        self.map_tiles[y][x] = "road"
                elif self.map_data[y][x] == 's':
                    ctx = self.map_ctx4(x,y,'s')
                    code = "s|%s%s%s%s" % (bool_sym(ctx[0]), bool_sym(ctx[1]), bool_sym(ctx[2]), bool_sym(ctx[3]))
                    if imgctl.tile_exists(code):
                        self.map_tiles[y][x] = code
                    else:
                        # No special tile -> better ugly than segfault
                        self.map_tiles[y][x] = "sand"
                else:
                    raise Exception("Unknown tile type %s" % (self.map_tiles[y][x]))
    # col -1 = col 0 etc
    def map_data_get(self, x, y):
        if x < 0:
            x = 0
        elif x >= self.sz_x:
            x = self.sz_x-1
        if y < 0:
            y = 0
        elif y >= self.sz_y:
            y = self.sz_y-1

        #print (x,y)
        #print len(self.map_data)
        #print len(self.map_data[y])
        return self.map_data[y][x]
    # 0 1 2
    # 3   4
    # 5 6 7
    def map_ctx(self, x, y):
        return (
          self.map_data_get(x-1,y-1),
          self.map_data_get(x  ,y-1),
          self.map_data_get(x+1,y-1),
          self.map_data_get(x-1,y  ),
          self.map_data_get(x+1,y  ),
          self.map_data_get(x-1,y+1),
          self.map_data_get(x  ,y+1),
          self.map_data_get(x+1,y+1)
        )
    # 0 _ 1
    # _ _ _
    # 2 _ 3
    def map_ctx4(self, x, y, t):
        ctx = self.map_ctx(x,y)
        ul = ctx[0] != t or ctx[1] != t or ctx[3] != t
        ur = ctx[1] != t or ctx[2] != t or ctx[4] != t
        dl = ctx[3] != t or ctx[5] != t or ctx[6] != t
        dr = ctx[4] != t or ctx[6] != t or ctx[7] != t
        return (ul, ur, dl, dr)
    def render(self, target, (ofs_x, ofs_y)):
        # Just to reduce the computations a little
        # Actually min/max is not necessary
        min_x = max(ofs_x / 64, 0)
        max_x = min((ofs_x+768+63)/64, self.sz_x-1)
        min_y = max(ofs_y / 48, 0)
        max_y = min((ofs_y+576+47)/48, self.sz_y-1)
        for y in range(min_y, max_y+1):
            for x in range(min_x, max_x+1):
                imgctl.render_map_tile(target, self.map_tiles[y][x], (64*x-ofs_x, 48*y-ofs_y))

###########################################################
# Map database controller                                 #
###########################################################

class MapDB:
    def __init__(self, map_db):
        self.map_db = map_db
    # There's only one map anyway :-)
    def get_map_data(self, map_id):
        return self.map_db[map_id]

###########################################################
# Data for ImgCtl                                         #
###########################################################

# key => filename, actions
sprites_def = {
    "freya"      : ("freya/", ["walking", "running", "looking", "attack", "tipping over"]),
    "doc"        : ("doc/", ["healing", "walking"]),
    "red_spider" : ("red_spider/", ["walking", "attack", "tipping over"]),
}
tilesets_def = {
    "ground"    : "images/grund_iso_tileset.png",
    "bush"      : "images/bushes_tileset.png",
    "trees"     : "images/trees_tileset.png",
    # Half of the tiles have different transparency than the other half, suxorz
#    "rocks"  : "/home/taw/reinerstileset/images/T rocks iso/rocks iso tileset.bmp",
    "rocks"     : "images/rocks_iso_tileset_-_bad.png",
    "farmhouse" : "images/farmhouse_iso_tileset.png",
    "foresters" : "images/foresters_lodge_fix_tileset_1.png",
    "temple"    : "images/small_temple_iso_tileset.png",
}

# All in units of 16x16: (file, ofs_x, ofs_y, sz_x, sz_y)
tiles_def = {
    "dirt"  : ("ground", 2*4, 9*3, 4, 3),
    "grass" : ("ground", 3*4, 9*3, 4, 3),

    "sand"  : ("ground", 4*4, 9*3, 4, 3),
    "s|----": ("ground", 4*4, 9*3, 4, 3),
    "s|+-+-": ("ground",12*4, 0*3, 4, 3),
    "s|--++": ("ground",13*4, 1*3, 4, 3),
    "s|-+-+": ("ground",12*4, 1*3, 4, 3),
    "s|++--": ("ground",13*4, 0*3, 4, 3),

    "s|+---": ("ground",10*4, 0*3, 4, 3),
    "s|-+--": ("ground",11*4, 0*3, 4, 3),
    "s|--+-": ("ground", 9*4, 0*3, 4, 3),
    "s|---+": ("ground", 8*4, 0*3, 4, 3),

    "s|+++-": ("ground", 8*4, 1*3, 4, 3),
    "s|-+++": ("ground", 9*4, 1*3, 4, 3),
    "s|+-++": ("ground",10*4, 1*3, 4, 3),
    "s|++-+": ("ground",11*4, 1*3, 4, 3),

    "road"  : ("ground", 5*4, 9*3, 4, 3),
    "r|----": ("ground", 5*4, 9*3, 4, 3),

    "r|+-+-": ("ground", 4*4, 10*3+2, 4, 3),
    "r|--++": ("ground", 5*4, 11*3+2, 4, 3),
    "r|-+-+": ("ground", 4*4, 11*3+2, 4, 3),
    "r|++--": ("ground", 5*4, 10*3+2, 4, 3),

    "r|+---": ("ground", 2*4, 10*3+2, 4, 3),
    "r|-+--": ("ground", 3*4, 10*3+2, 4, 3),
    "r|--+-": ("ground", 1*4, 10*3+2, 4, 3),
    "r|---+": ("ground", 0*4, 10*3+2, 4, 3),

    "r|+++-": ("ground", 0*4,11*3+2, 4, 3),
    "r|-+++": ("ground", 1*4,11*3+2, 4, 3),
    "r|+-++": ("ground", 2*4,11*3+2, 4, 3),
    "r|++-+": ("ground", 3*4,11*3+2, 4, 3),

    "water" : ("ground", 6*4, 9*3, 4, 3),
    "w|----": ("ground", 6*4, 9*3, 4, 3),
    "w|+-+-": ("ground",12*4,10*3+2, 4, 3),
    "w|--++": ("ground",13*4,11*3+2, 4, 3),
    "w|-+-+": ("ground",12*4,11*3+2, 4, 3),
    "w|++--": ("ground",13*4,10*3+2, 4, 3),

    "w|+---": ("ground",10*4,10*3+2, 4, 3),
    "w|-+--": ("ground",11*4,10*3+2, 4, 3),
    "w|--+-": ("ground", 9*4,10*3+2, 4, 3),
    "w|---+": ("ground", 8*4,10*3+2, 4, 3),

    "w|+++-": ("ground", 8*4,11*3+2, 4, 3),
    "w|-+++": ("ground", 9*4,11*3+2, 4, 3),
    "w|+-++": ("ground",10*4,11*3+2, 4, 3),
    "w|++-+": ("ground",11*4,11*3+2, 4, 3),

    "plant 1": ("bush", 0,   7*4, 4, 4),
    "plant 2": ("bush", 4*4, 7*4, 4, 4),
    "plant 3": ("bush", 0,   8*4, 4, 4),
    "plant 4": ("bush", 0,  10*4, 4, 4),

    "cactus 1":("bush", 5*4, 45, 4, 4),
    "cactus 2":("bush", 6*4, 45, 4, 4),
    "cactus 3":("bush", 7*4, 45, 4, 4),
    "cactus 4":("bush", 2*4,9*4, 4, 4),
    "cactus 5":("bush", 3*4,9*4, 4, 4),
    "cactus 6":("bush", 4*4,9*4, 4, 4),
    "cactus 7":("bush", 5*4,9*4, 4, 4),
    "cactus 8":("bush", 6*4,9*4, 4, 4),


    "tree 1" : ("trees", 0*8, 0*8, 8, 8),
    "tree 2" : ("trees", 1*8, 0*8, 8, 8),
    "tree 3" : ("trees", 2*8, 0*8, 8, 8),
    "tree 4" : ("trees", 3*8, 0*8, 8, 8),
    "tree 5" : ("trees", 0*8, 1*8, 8, 8),
    "tree 6" : ("trees", 1*8, 1*8, 8, 8),
    "tree 7" : ("trees", 2*8, 1*8, 8, 8),
    "tree 8" : ("trees", 3*8, 1*8, 8, 8),
    "tree 9" : ("trees", 0*8, 2*8, 8, 8),
    "tree 10": ("trees", 1*8, 2*8, 8, 8),
    "tree 11": ("trees", 2*8, 2*8, 8, 8),
    "tree 12": ("trees", 3*8, 2*8, 8, 8),
    "tree 13": ("trees", 0*8, 3*8, 8, 8),
    "tree 14": ("trees", 1*8, 3*8, 8, 8),
    "tree 15": ("trees", 2*8, 3*8, 8, 8),
    "tree 16": ("trees", 3*8, 3*8, 8, 8),
    "tree 17": ("trees", 0*8, 4*8, 8, 8),
    "tree 18": ("trees", 1*8, 4*8, 8, 8),
    "tree 19": ("trees", 2*8, 4*8, 8, 8),
    "tree 20": ("trees", 3*8, 4*8, 8, 8),
    "tree 21": ("trees", 0*8, 5*8, 8, 8),
    "tree 22": ("trees", 1*8, 5*8, 8, 8),
    "tree 23": ("trees", 2*8, 5*8, 8, 8),
    "tree 24": ("trees", 3*8, 5*8, 8, 8),

    "bridge H" : ("rocks", 48, 32+2, 16, 16-4),
    "bridge V" : ("rocks", 48+2, 48, 16-4, 16),

    "farmhouse L" : ("farmhouse", 0, 0, 20, 18),
    "farmhouse C" : ("farmhouse", 0,18, 20, 18),
    "farmhouse R" : ("farmhouse", 0,36, 20, 18),

    "hut light L" : ("foresters", 0, 0, 16, 18),
    "hut light R" : ("foresters",16, 0, 16, 18),
    "hut light Lo": ("foresters", 0,18, 16, 18),
    "hut light Ro": ("foresters",16,18, 16, 18),
    "hut mid L"   : ("foresters", 0,36, 16, 18),
    "hut mid R"   : ("foresters",16,36, 16, 18),
    "hut mid Lo"  : ("foresters",32, 0, 16, 18),
    "hut dark Lo" : ("foresters",48, 0, 16, 18),
    "hut mid Ro"  : ("foresters",32,18, 16, 18),
    "hut dark Ro" : ("foresters",48,18, 16, 18),
    "hut dark L"  : ("foresters",32,36, 16, 18),
    "hut dark R"  : ("foresters",48,36, 16, 18),

    "temple silver L" : ("temple", 0, 0, 16, 18),
    "temple gold L"   : ("temple",16, 0, 16, 18),
    "temple black L"  : ("temple",32, 0, 16, 18),
    "temple blue L"   : ("temple",48, 0, 16, 18),
    "temple silver R" : ("temple", 0,18, 16, 18),
    "temple gold R"   : ("temple",16,18, 16, 18),
    "temple black R"  : ("temple",32,18, 16, 18),
    "temple blue R"   : ("temple",48,18, 16, 18),
    "temple silver C" : ("temple", 0,36, 16, 18),
    "temple gold C"   : ("temple",16,36, 16, 18),
    "temple black C"  : ("temple",32,36, 16, 18),
    "temple blue C"   : ("temple",48,36, 16, 18),
}

###########################################################
# Properties of various objects                           #
###########################################################

# object => halfsize_x, halfsize_y, valence
# valence = 1 (bridge), 0 (ignore), -1 (obstacle)
object_properties = {
"tree 1"  : (2*16, 2*16,-1),
"tree 2"  : (2*16, 2*16,-1),
"tree 2"  : (2*16, 2*16,-1),
"tree 3"  : (2*16, 2*16,-1),
"tree 4"  : (2*16, 2*16,-1),
"tree 5"  : (2*16, 2*16,-1),
"tree 6"  : (2*16, 2*16,-1),
"tree 7"  : (2*16, 2*16,-1),
"tree 8"  : (2*16, 2*16,-1),
"tree 9"  : (2*16, 2*16,-1),
"tree 10" : (2*16, 2*16,-1),
"tree 11" : (2*16, 2*16,-1),
"tree 12" : (2*16, 2*16,-1),
"tree 13" : (2*16, 2*16,-1),
"tree 14" : (2*16, 2*16,-1),
"tree 15" : (2*16, 2*16,-1),
"tree 16" : (2*16, 2*16,-1),
"tree 17" : (2*16, 2*16,-1),
"tree 18" : (2*16, 2*16,-1),
"tree 19" : (2*16, 2*16,-1),
"tree 20" : (2*16, 2*16,-1),
"tree 21" : (2*16, 2*16,-1),
"tree 22" : (2*16, 2*16,-1),
"tree 23" : (2*16, 2*16,-1),
"tree 24" : (2*16, 2*16,-1),
# Make plants non-obstacles to reduce annoyance level
#"plant 1" : (2*16, 2*16,-1),
#"plant 2" : (2*16, 2*16,-1),
#"plant 3" : (2*16, 2*16,-1),
#"plant 4" : (2*16, 2*16,-1),

# Cacti are rare enough not to be overly annoying
"cactus 1" : (2*16, 2*16, -1),
"cactus 2" : (2*16, 2*16, -1),
"cactus 3" : (2*16, 2*16, -1),
"cactus 4" : (2*16, 2*16, -1),
"cactus 5" : (2*16, 2*16, -1),
"cactus 6" : (2*16, 2*16, -1),
"cactus 7" : (2*16, 2*16, -1),
"cactus 8" : (2*16, 2*16, -1),


"bridge H"     : (8*16, 4*16, 1),
"bridge V"     : (4*16, 8*16, 1),

# The actual shapes are not even rectangular
"hut mid L"    : (6*16, 6*16, -1),
"temple blue R": (6*16, 6*16, -1),
"farmhouse L"  : (6*16, 6*16, -1),
"hut dark R"   : (6*16, 6*16, -1),
"farmhouse R"  : (6*16, 6*16, -1),
"hut light L"  : (6*16, 6*16, -1),
}

###########################################################
# Global Image controller object                          #
###########################################################
imgctl = ImgCtl(sprites_def, tilesets_def, tiles_def)

###########################################################
# The map database itself                                 #
###########################################################

# "Abstract" map
map_main_abstract_tiles = [
"wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww",
"www              ww                wwwww",
"ww               ww                  www",
"w                ww                    w",
"w                wwwwwww               w",
"w                wwwwwww               w",
"w                     ww               w",
"w                     ww               w",
"w            wwwwwwwwwww               w",
"w            wwwwwwwwwww               w",
"w                                      w",
"w                                      w",
"w                                      w",
"w                                      w",
"w                                      w",
"w                                      w",
"w                                      w",
"w                                      w",
"w                                      w",
"w                                      w",
"w                          rr          w",
"w                          rrr         w",
"w                          rrr  rr     w",
"w                           rrr rr     w",
"w                            rrrrr     w",
"w                        rrr rrrrr     w",
"w                        rrrrrrr    rr w",
"w                         rrrrrr   rrr w",
"w                             rrrrrrr  w",
"w                            rrrrrrr   w",
"w                            rrr       w",
"w                            rr        w",
"w                            rrr       w",
"w                            rrr       w",
"w                         rr  rr       w",
"w                         rrrrrr   rr  w",
"w                          rrrrrrrrrr  w",
"ww                            rrrrrr  ww",
"wwww                          rr     www",
"wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww",
"wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww",
"wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww",
"wwwwwwwwwwwwwwwwwssssssssss   rr wwwwwww",
"wwwwssssssssssssssssssssssss  rr     www",
"wwsssssssssssssssssssssssssss rr    sssw",
"wssssssssssssssssssssssssssss     sssssw",
"wssssssssssssssssssssssssssssss sssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wssssssssssssssssssssssssssssssssssssssw",
"wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww",
]

# Location in 16-blocks
map_main_objects_old = [
    ("bridge", 28,24), # 16 12
    ("plant 1",20,10), # 4 4
    ("plant 2",15,20),
    ("tree 1", 32,17), # 8 8
    ("plant 3",37,27),
    ("plant 4",34,11),
]
map_main_objects = [
    ("hut mid L",    111,  61),
    ("temple blue R",139,  64),
    ("farmhouse L",  101,  72),
    ("hut dark R",   149,  78),
    ("farmhouse R",  147, 102),
    ("hut light L",  107, 102),
    ("bridge V",     124, 121),
]
i=0
while i < 400:
    x = randint(3,40*4-4)
    y = randint(3,40*3-4)
    # Leave some space for the village
    if x > 23*4 and y > 16*3:
        continue
    obj = choice(["plant 1", "plant 2", "plant 3", "plant 4",
                              "plant 1", "plant 2", "plant 3", "plant 4",
                          "plant 1", "plant 2", "plant 3", "plant 4",
                          "plant 1", "plant 2", "plant 3", "plant 4",
                          "plant 1", "plant 2", "plant 3", "plant 4",
                          "plant 1", "plant 2", "plant 3", "plant 4",
                  "tree 1", "tree 2", "tree 3", "tree 4",
                  "tree 5", "tree 6", "tree 7", "tree 8",
                  "tree 9", "tree 10", "tree 11", "tree 12",
                  "tree 13", "tree 14", "tree 15", "tree 16",
                  "tree 17", "tree 18", "tree 19", "tree 20",
                  "tree 21", "tree 22", "tree 23", "tree 24"
                 ])
    map_main_objects.append((obj,x,y))
    i += 1
i=0
while i < 50:
    x = randint(3,40*4-4)
    y = randint(40*3+15,70*3-10)
    obj = choice(["cactus 1", "cactus 2", "cactus 3", "cactus 4",
                  "cactus 5", "cactus 6", "cactus 7", "cactus 8",
    ])
    map_main_objects.append((obj,x,y))
    i += 1

# I don't know if it should be y or -y ^_^
# FIXME: Actually it shouldn't be like that at all
# NPC and map object display should be interleaved
sortby(map_main_objects, lambda (obj_type, x, y): (y, x))

map_main = (40,70,map_main_abstract_tiles,map_main_objects)

mapdb = MapDB({
    "main" : map_main,
})
