#!/usr/bin/python
# -*- coding: UTF-8 -*-

import warnings

###########################################################
# Global tile data                                        #
###########################################################
ctdir = {
    "arab-trader" : "arab-trader.png", # Oasis
    "elf-monk"    : "elf-monk.png",    # The library
    "elf-trader"  : "elf-trader.png",  # The castle road
    "female-blue" : "female-blue.png", # Main chara
    "king"        : "king.png",        # Throne room in the Castle
    "nurse"       : "nurse.png",       # Hospital
    "soldier-axe" : "soldier-axe.png", # The castle
    "soldier-elf" : "soldier-elf.png", # Elven town
    "wizard-gray" : "wizard-gray.png", # Wizard hut in the Elven town
    "angel-blue"  : "angel-blue.png",  # Guardian angel of Software Development
    "dwarf-smith" : "dwarf-smith.png"  # Dwarf smith
#    "man-worker"  : "man-worker.png",  # NOT USED
}
mtctl_terrain = {
# Movable terrain
  ' ' : (  9, 23, False), # grass
  's' : ( 12, 23, False), # sand
  'h' : ( 93, 23, False), # hilly land
  '.' : ( 30, 23, False), # (stone) road
  ',' : ( 27, 23, False), # dungeon floor
  'D' : ( 67, 25, False), # Doors (brick)
  'd' : ( 81, 25, False), # Doors (blue)
  'V' : ( 96, 24, False), # Doors (wooden)
  'k' : ( 32, 26, False), # gate, opne
  '_' : ( 84, 23, False), # Snowy land
  'H' : ( 96, 23, False), # Icy hilly land
  '>' : ( 28, 26, False), # stairs up
  '<' : ( 29, 26, False), # stairs down
# Blocking terrain
  ':' : ( 30, 23, True),  # (stone) road - special version that can block you ;-)
  't' : ( 54, 23, True),  # tree
  'T' : ( 60, 23, True),  # pine tree
  'm' : (117, 23, True),  # mountain
  'r' : ( 96, 21, True),  # rocks
  '~' : ( 18, 23, True),  # water
  'P' : ( 69, 23, True),  # palm tree
  'C' : ( 99, 22, True),  # cactus
  'i' : (105, 22, True),  # dead desert tree
  'j' : (123, 23, True),  # desert mountain
  'b' : ( 99, 24, True),  # brick wall
  'S' : (105, 24, True),  # stone wall
  'W' : (111, 24, True),  # wooden wall
  'B' : ( 78, 25, True),  # Blue brick wall
  'K' : ( 30, 26, True),  # gate, closed
  'z' : ( 72, 24, True),  # Window in a brick wall
  'Z' : ( 75, 24, True),  # Window in a stone wall
  'M' : ( 87, 23, True),  # Icy mountain
  'Q' : ( 90, 23, True),  # Icy tree
  'E' : (120, 24, True),  # Red brick wall
# Map edges
  'x' : (  0,  0, True),  # map border
  'X' : (  0,  0, False), # enter-able map border (must add event here)
}
mtctl_enemies = {
  # Rats
  "white rat"       : (24, 13),
  "black rat"       : (25, 13),
  "brown rat"       : (26, 13),
  "red rat"         : (27, 13),
  # Frogs
  "green frog"      : ( 8, 19),
  "red frog"        : ( 9, 19),
  # Lizards
  "spotty lizard"   : (12, 19),
  "red lizard"      : (13, 19),
  "brown lizard"    : (14, 19),
  "black lizard"    : (15, 19),
  "green lizard"    : (16, 19),
  # Eagles
  "eagle 1"         : (12, 17),
  "eagle 2"         : (13, 17),
  "eagle 3"         : (14, 17),
  "eagle 4"         : (15, 17),
  # Basilisks
  "basilisk 1"      : ( 8, 17),
  "basilisk 2"      : ( 9, 17),
  "basilisk 3"      : (10, 17),
  "basilisk 4"      : (11, 17),
  # Vultures
  "vulture 1"       : (35, 19),
  "vulture 2"       : (36, 19),
  "vulture 3"       : (37, 19),
  # Turtles
  "green turtle"    : (66, 18),
  "red turtle"      : (67, 18),
  "black turtle"    : (68, 18),
  "brown turtle"    : (69, 18),
  "blue turtle"     : (70, 18),
  "yellow turtle"   : (71, 18),
  # Scorpions
  "red scoprion"    : (72, 18),
  "yellow scoprion" : (73, 18),
  "gray scoprion"   : (74, 18),
  "blue scoprion"   : (75, 18),
  "brown scoprion"  : (76, 18),
  "black scoprion"  : (77, 18),
  # Dogs
  "dog 1"           : (72, 15),
  "dog 2"           : (73, 15),
  "dog 3"           : (74, 15),
  "dog 4"           : (75, 15),
  "dog 5"           : (76, 15),
  "dog 6"           : (77, 15),
  # Spiders
  "spider 1"        : (50, 15),
  "spider 2"        : (51, 15),
  "spider 3"        : (52, 15),
  "spider 4"        : (53, 15),
  "spider 5"        : (54, 15),
  "spider 6"        : (55, 15),
  "spider 7"        : (56, 15),
  # Bats
  "bat 1"           : ( 0, 16),
  "bat 2"           : ( 1, 16),
  "bat 3"           : ( 2, 16),
  "bat 4"           : ( 3, 16),
  "bat 5"           : ( 4, 16),
  # Snakes
  "snake 1"         : (13, 16),
  "snake 2"         : (14, 16),
  "snake 3"         : (15, 16),
  "snake 4"         : (16, 16),
  "snake 5"         : (17, 16),
  "snake 6"         : (18, 16),
  "snake 7"         : (19, 16),
  "snake 8"         : (20, 16),
  "snake 9"         : (21, 16),
  "snake 10"        : (22, 16),
  "snake 11"        : (23, 16),
  "snake 12"        : (24, 16),
  "snake 13"        : (25, 16),
  "snake 14"        : (26, 16),
  "snake 15"        : (27, 16),
  "snake 16"        : (28, 16),
  "snake 17"        : (29, 16),
  "snake 18"        : (30, 16),
  "snake 19"        : (31, 16),
  "snake 20"        : (32, 16),
  # Skeletons 
  "skeleton 1"      : (28, 20),
  "skeleton 2"      : (29, 20),
  "skeleton 3"      : (30, 20),
  "skeleton 4"      : (31, 20),
  "skeleton 5"      : (32, 20),
  "skeleton 6"      : (33, 20),
  "skeleton 7"      : (34, 20),
  "skeleton sw 1"   : (35, 20),
  "skeleton sw 2"   : (36, 20),
  "skeleton sb 1"   : (37, 20),
  "skeleton sb 2"   : (38, 20),
  "skeleton 2sw"    : (39, 20),
  "skeleton 2sb"    : (40, 20),
  "skeleton sw sh"  : (41, 20),
  "skeleton sb sh"  : (42, 20),
  "skeleton cloak 1": (43, 20),
  "skeleton cloak 2": (44, 20),
  "skeleton cloak 3": (45, 20),
  "skeleton cloak 4": (46, 20),
  "skeleton wiz 1"  : (47, 20),
  "skeleton wiz 2"  : (48, 20),
  "skeleton wiz 3"  : (49, 20),
  "skeleton orc 1"  : (54, 20),
  "skeleton orc 2"  : (55, 20),
  "skeleton orc 3"  : (56, 20),
  "skeleton orc 4"  : (57, 20),
  "skeleton orc 5"  : (58, 20),
  "skeleton dwf 1"  : (59, 20),
  "skeleton dwf 2"  : (60, 20),
  "skeleton 3glav"  : (61, 20),
  "skeleton small"  : (62, 20),
  # Bears
  "bear 1"          : (32, 19),
  "bear 2"          : (33, 19),
  # Dragons
  "dragon tiny 1"   : ( 0, 12),
  "dragon tiny 2"   : ( 1, 12),
  "dragon tiny 3"   : ( 2, 12),
  "dragon tiny 4"   : ( 3, 12),
  "dragon tiny 5"   : ( 4, 12),
  "dragon tiny 6"   : ( 5, 12),
  "dragon tiny 7"   : ( 6, 12),
  "dragon tiny 8"   : ( 7, 12),
  "dragon small 1"  : ( 8, 12),
  "dragon small 2"  : ( 9, 12),
  "dragon small 3"  : (10, 12),
  "dragon small 4"  : (11, 12),
  "dragon small 5"  : (12, 12),
  "dragon small 6"  : (13, 12),
  "dragon small 7"  : (14, 12),
  "dragon small 8"  : (15, 12),
  "dragon normal 1" : (16, 12),
  "dragon normal 2" : (17, 12),
  "dragon normal 3" : (18, 12),
  "dragon normal 4" : (19, 12),
  "dragon normal 5" : (20, 12),
  "dragon normal 6" : (21, 12),
  "dragon normal 7" : (22, 12),
  "dragon normal 8" : (23, 12),
  "dragon big 1"    : (24, 12),
  "dragon big 2"    : (25, 12),
  "dragon big 3"    : (26, 12),
  "dragon big 4"    : (27, 12),
  "dragon big 5"    : (28, 12),
  "dragon big 6"    : (29, 12),
  "dragon big 7"    : (30, 12),
  "dragon big 8"    : (31, 12),
  # Orcs
  "orc 1"           : (11, 13),
  "orc 2"           : (12, 13),
  "orc 3"           : (13, 13),
}
mtctl_items = {
  "copper coins"    : ( 7,  7),
  "silver coins"    : ( 8,  7),
  "golden coins"    : ( 9,  7),
  "blue crystals"   : (14,  7),
  "pickaxe"         : (27,  7),
  "skull"           : (43,  7),
  "bones"           : (44,  7),
  "skeleton 1"      : (45,  7),
  "skeleton 2"      : (46,  7),
  "skeleton 3"      : (47,  7),
  "skeleton 4"      : (48,  7),
  "skeleton 5"      : (49,  7),
  "skeleton 6"      : (50,  7),
  "black mushroom"  : ( 7,  2),
  "white mushroom"  : ( 8,  2),
  "gray mushroom"   : ( 9,  2),
  "orange mushroom" : (10,  2),
  "red mushroom"    : (11,  2),
  "green mushroom"  : (12,  2),
  "blue mushroom"   : (13,  2),
  "Dbrown mushroom" : (14,  2),
  "black mushroom 2": (15,  2),
  "gray mushroom 2" : (16,  2),
  "violet mushroom" : (17,  2),
  "yellow mushroom" : (18,  2),
  "red mushroom 2"  : (20,  2),
  "green mushroom 2": (21,  2),
  "cyan mushroom"   : (22,  2),
  "Lbrown mushroom" : (23,  2),
  "spellbook gray 1": ( 9,  6),
  "spellbook gray 2": (10,  6),
  "spellbook gray 3": (11,  6),
  "spellbook gray 4": (12,  6),
  "spellbook gray 5": (13,  6),
  "spellbook gray 6": (14,  6),
  "spellbook gray 7": (15,  6),
  "spellbook gray 8": (16,  6),
  "spellbook gray 9": (17,  6),
  "spellbook blue 1": (18,  6),
  "spellbook blue 2": (19,  6),
  "spellbook blue 3": (20,  6),
  "spellbook blue 4": (21,  6),
  "spellbook blue 5": (22,  6),
  "spellbook blue 6": (23,  6),
  "spellbook blue 7": (24,  6),
  "spellbook blue 8": (25,  6),
  "spellbook blue 9": (26,  6),
  "spellbook green 1":(27,  6),
  "spellbook green 2":(28,  6),
  "spellbook green 3":(29,  6),
  "spellbook green 4":(30,  6),
  "spellbook green 5":(31,  6),
  "spellbook green 6":(32,  6),
  "spellbook green 7":(33,  6),
  "spellbook green 8":(34,  6),
  "spellbook green 9":(35,  6),
  "spellbook red 1" : (36,  6),
  "spellbook red 2" : (37,  6),
  "spellbook red 3" : (38,  6),
  "spellbook red 4" : (39,  6),
  "spellbook red 5" : (40,  6),
  "spellbook red 6" : (41,  6),
  "spellbook red 7" : (42,  6),
  "spellbook red 8" : (43,  6),
  "spellbook red 9" : (44,  6),
  "spellbook cyan 1" :(45,  6),
  "spellbook cyan 2" :(46,  6),
  "spellbook cyan 3" :(47,  6),
  "spellbook cyan 4" :(48,  6),
  "spellbook cyan 5" :(49,  6),
  "spellbook cyan 6" :(50,  6),
  "spellbook cyan 7" :(51,  6),
  "spellbook cyan 8" :(52,  6),
  "spellbook cyan 9" :(53,  6),
  "spellbook pink 1" :(54,  6),
  "spellbook pink 2" :(55,  6),
  "spellbook pink 3" :(56,  6),
  "spellbook pink 4" :(57,  6),
  "spellbook pink 5" :(58,  6),
  "spellbook pink 6" :(59,  6),
  "spellbook pink 7" :(60,  6),
  "spellbook pink 8" :(61,  6),
  "spellbook pink 9" :(62,  6),
  "potion 1"        : ( 0,  8),
  "potion 2"        : ( 1,  8),
  "potion 3"        : ( 2,  8),
  "potion 4"        : ( 3,  8),
  "potion 5"        : ( 4,  8),
  "potion 6"        : ( 5,  8),
  "potion 7"        : ( 6,  8),
  "potion 8"        : ( 7,  8),
  "potion 9"        : ( 8,  8),
  "potion 10"       : ( 9,  8),
  "potion 11"       : (10,  8),
  "potion 12"       : (11,  8),
  "potion 13"       : (12,  8),
  "potion 14"       : (13,  8),
  "potion 15"       : (14,  8),
  "potion 16"       : (15,  8),
  "potion 17"       : (16,  8),
  "potion 18"       : (17,  8),
  "potion 19"       : (18,  8),
  "potion 20"       : (19,  8),
  "potion 21"       : (20,  8),
  "potion 22"       : (21,  8),
  "potion 23"       : (22,  8),
  "potion 24"       : (23,  8),
  "potion 25"       : (24,  8),
  "potion 26"       : (25,  8),
  # And there are more potions ...
  "magical symbol R": (39,  7),
  "magical symbol Y": (40,  7),
  "magical symbol G": (41,  7),
  "star 1"          : (48,  1),
  "star 2"          : (49,  1),
  "star 3"          : (50,  1),
  "star 4"          : (51,  1),
  "star 5"          : (52,  1),
  "star 6"          : (53,  1),
  "star 7"          : (54,  1),
  "star 8"          : (55,  1),
  "star 9"          : (56,  1),
  "star 10"         : (57,  1),
  "star 11"         : (58,  1),
  "star 12"         : (59,  1),
  # Treasure chests
  "chest 1"         : ( 0,  7),
  "chest 2"         : ( 1,  7),
  "chest 3"         : ( 2,  7),
  "chest 4"         : ( 3,  7),
  "chest 5"         : ( 4,  7),
  "chest 6"         : ( 5,  7),
  "crystal ball"    : (42,  5),
  # Swords
  "broken sword"    : ( 2, 10),
  "sword"           : (16, 10),
  "magic sword"     : (17, 10),
  "hammer"          : (19, 10),
}
# TODO: find nicer indoor tiles
# area => (background_image, active_font_color, inactive_font_color) list
battle_look_table = {
    "forest" : [# CC-BY-SA by Retinafunk, http://www.flickr.com/photos/retinafunk/66237672/
                ("images/bg-forestsunrise.jpg", (255, 255, 127), (0, 255, 127)),
                # CC-BY-SA by Retinafunk, http://www.flickr.com/photos/retinafunk/66241775/
                ("images/bg-blueforestroad.jpg", (255, 255, 0), (0, 255, 0))],
    "desert" : [# CC-BY-SA by Rosino, http://www.flickr.com/photos/rosino/84514003/
                ("images/bg-desert.jpg", (255, 255, 127), (0, 255, 85))],
    "ice"    : [# CC-BY by Paul Keller, http://www.flickr.com/photos/paulk/82801769/
                ("images/bg-ice.jpg", (255, 255, 127), (0, 0, 0))],
# TODO: hills copied from ice, find some new graphics
    "hills"  : [# CC-BY by Paul Keller, http://www.flickr.com/photos/paulk/82801769/
                ("images/bg-ice.jpg", (255, 255, 127), (0, 0, 0))],
    "marsh"  : [# CC-BY by v8hotty, http://www.flickr.com/photos/givingearth/65855880/
                ("images/bg-marsh.jpg", (255, 255, 0), (0, 255, 0)),
                # CC-BY by eye of einstein, http://www.flickr.com/photos/35188692@N00/73762475/
                ("images/bg-sadbluetree.jpg", (250, 0, 255), (0, 0, 255))],
    "tower"  : [# CC-BY-SA by dboy, http://www.flickr.com/photos/dannyboyster/28978194/
                ("images/bg-stonewall.jpg", (0, 255, 255), (0, 0, 255))],
    "dungeon": [# CC-BY by eye of einstein, http://www.flickr.com/photos/35188692@N00/72553827/
                ("images/bg-coldlava.jpg", (255, 255, 127), (0, 0, 255))]
}
