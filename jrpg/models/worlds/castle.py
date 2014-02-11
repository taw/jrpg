# -*- coding: UTF-8 -*-

from random import choice, randint


tower_enemies = [
    "spider 1",
    "spider 2",
    "spider 3",
    "spider 4",
    "spider 5",
    "spider 6",
    "spider 7",
    "bat 1",
    "bat 2",
    "bat 3",
    "bat 4",
    "bat 5",
    "snake 1",
    "snake 2",
    "snake 3",
    "snake 4",
    "snake 5",
    "snake 6",
    "snake 7",
    "snake 8",
    "snake 9",
    "snake 10",
    "snake 11",
    "snake 12",
    "snake 13",
    "snake 14",
    "snake 15",
    "snake 16",
    "snake 17",
    "snake 18",
    "snake 19",
    "snake 20",
]

dungeon_lvl_1_decorations = [
    "skull",
    "bones",
    "skeleton 1",
    "skeleton 2",
    "skeleton 3",
    "skeleton 4",
    "skeleton 5",
    "skeleton 6",
]
# Add some cool enemies maybe
dungeon_lvl_1_enemies = [
    "white rat",
    "black rat",
    "brown rat",
    "red rat",
    "red scoprion",
    "yellow scoprion",
    "gray scoprion",
    "blue scoprion",
    "brown scoprion",
    "black scoprion",
    "skeleton 1",
    "skeleton 2",
    "skeleton 3",
    "skeleton 4",
    "skeleton 5",
    "skeleton 6",
    "skeleton 7",
    "skeleton sw 1",
    "skeleton sw 2",
    "skeleton sb 1",
    "skeleton sb 1",
    "skeleton 2sw",
    "skeleton 2sb",
    "skeleton sw sh",
    "skeleton sb sh",
    "basilisk 1",
    "basilisk 2",
    "basilisk 3",
    "basilisk 4",
]
dungeon_lvl_2_decorations = [
    "skull",
    "bones",
    "skeleton 1",
    "skeleton 2",
    "skeleton 3",
    "skeleton 4",
    "skeleton 5",
    "skeleton 6",
]
dungeon_lvl_2_enemies = [
    "skeleton sw 1",
    "skeleton sw 2",
    "skeleton sb 1",
    "skeleton sb 1",
    "skeleton 2sw",
    "skeleton 2sb",
    "skeleton sw sh",
    "skeleton sb sh",
    "basilisk 1",
    "basilisk 2",
    "basilisk 3",
    "basilisk 4",
    "orc 1",
    "orc 2",
    "orc 3",
    "skeleton orc 1",
    "skeleton orc 2",
    "skeleton orc 3",
]
dungeon_lvl_3_decorations = [
    "skull",
    "bones",
    "skeleton 1",
    "skeleton 2",
    "skeleton 3",
    "skeleton 4",
    "skeleton 5",
    "skeleton 6",
]
dungeon_lvl_3_enemies = [
    "skeleton wiz 1",
    "skeleton wiz 2",
    "skeleton wiz 3",
    "skeleton orc 4",
    "skeleton orc 5",
    "skeleton dwf 1",
    "skeleton dwf 2",
    "skeleton 3glav",
    "skeleton small",
    "dragon tiny 1",
    "dragon tiny 2",
    "dragon tiny 3",
    "dragon tiny 4",
    "dragon tiny 5",
    "dragon tiny 6",
    "dragon tiny 7",
    "dragon small 1",
    "dragon small 2",
    "dragon small 3",
    "dragon small 4",
    "dragon small 5",
    "dragon small 6",
    "dragon small 7",
]


#####################################################################
# Castle                                                            #
#####################################################################
class World_castle:
    def __init__(self, wm, ui, mhc):
        wm.wormhole((4, 9), "world", (7, 9))
        king_already_said_something = [False]
        
        def king_event():
            if king_already_said_something[0]:
                return
            # Dungeon not even opened
            if not mhc.quest_is_done("dungeon gate open"):
                ui.change_text([
                    U"Please help. Kanji monsters stole all the kingdom's treasures.",
                    U"They're in castle dungeon, but it's impossible to go there now.",
                    U"Only the red spellbook can open the dungeon gate.",
                    U"It's probably in the castle tower, east from here.",
                ])
                king_already_said_something[0] = True
                return
            # Dungeon opened, no level cleaned
            if not mhc.quest_is_done("dungeon level 2 open"):
                ui.change_text([
                    U"Please find all the stolen treasures.",
                    U"You will get rewarded for it.",
                    U"When you find all treasures on one level, another will open."
                ])
                king_already_said_something[0] = True
                return
            # Level 1 cleaned, no reward yet
            if mhc.quest_is_done("dungeon level 2 open") and not mhc.quest_is_done("reward for level 1"):
                mhc.quest_do("reward for level 1")
                ui.change_text([
                    U"Please take this 100 coin reward for retrieving all",
                    U"the treasures from the first level.",
                    U"You will be rewarded for further levels too."
                ])
                king_already_said_something[0] = True
                mhc.receive_money(100)
                return
            # Level 1 cleaned and rewarded
            if not mhc.quest_is_done("dungeon level 3 open"):
                ui.change_text([
                    U"Please find all the stolen treasures.",
                    U"You will get rewarded for it.",
                    U"When you find all treasures on one level, another will open."
                ])
                king_already_said_something[0] = True
                return
            # Level 2 cleaned, no reward yet
            if mhc.quest_is_done("dungeon level 3 open") and not mhc.quest_is_done("reward for level 2"):
                mhc.quest_do("reward for level 2")
                ui.change_text([
                    U"Please take this 200 coin reward for retrieving all",
                    U"the treasures from the second level.",
                    U"You will be rewarded for further levels too."
                ])
                king_already_said_something[0] = True
                mhc.receive_money(200)
                return
            # Level 2 cleaned and rewarded
            if not mhc.quest_is_done("dungeon finished"):
                ui.change_text([
                    U"Please find all the stolen treasures on the last level.",
                    U"You will get rewarded for it.",
                ])
                king_already_said_something[0] = True
                return
            # Level 3 cleaned, no reward yet
            if mhc.quest_is_done("dungeon finished") and not mhc.quest_is_done("reward for level 3"):
                mhc.quest_do("reward for level 3")
                ui.change_text([
                    U"Please take this 300 coin reward for retrieving all",
                    U"the treasures from the last level.",
                    U"Thank you for the good work.",
                ])
                king_already_said_something[0] = True
                mhc.receive_money(300)
                return
            # Dungeon cleaned and rewarded
            if mhc.quest_is_done("dungeon finished"):
                ui.change_text([
                    U"Thanks for retrieving the treasures.",
                ])
                king_already_said_something[0] = True
                return
        wm.add_chara("king",route=[(2,2), (7,2), (7,5), (2,5)],event=king_event)
        treasures = [(i+1,  "chest 1", 2+i,   1) for i in range(6)] \
                  + [(i+7,  "chest 2",   1, 2+i) for i in range(4)] \
                  + [(i+11, "chest 2",   8, 2+i) for i in range(4)] \
                  + [(i+15, "chest 4", 3+i,   3) for i in range(4)] \
                  + [(i+19, "chest 4", 4+i,   4) for i in range(2)]
        for (chest_num, chest_type, x, y) in treasures:
            quest_id = "treasure %d" % chest_num
            if mhc.quest_is_done(quest_id):
                wm.add_decoration((x,y), chest_type)
        looked_into_crystal_ball = [False]
        def look_into_crystal_ball():
            # Don't perform useless recomputations
            if looked_into_crystal_ball[0]:
                return
            looked_into_crystal_ball[0] = True
            kanji_knowledge = mhc.get_kanji_knowledge()
            kanji_count = 0
            for k in kanji_knowledge: kanji_count += k
            ui.change_text([u"You look into the crystal ball and see:",
                            u"You know %d kanji perfectly, %d (%d) very well," % (kanji_knowledge[4], kanji_knowledge[3], kanji_knowledge[3]+kanji_knowledge[4]),
                            u"%d (%d) pretty well, %d (%d) only a bit," % (kanji_knowledge[2], kanji_knowledge[2]+kanji_knowledge[3]+kanji_knowledge[4], kanji_knowledge[1], kanji_knowledge[1]+kanji_knowledge[2]+kanji_knowledge[3]+kanji_knowledge[4]),
                            u"and %d of %d not at all." % (kanji_knowledge[0], kanji_count)
                            ])
        def finish_dungeon_gate_quest():
            if not mhc.quest_is_done("ice artifact"):
                ui.change_text([U"The dungeon gate is closed."])
            elif not mhc.quest_is_done("dungeon gate open"):
                ui.change_text([U"You use the red spellbook to open the dungeon gate."])
                mhc.quest_do("dungeon gate open")
                dungeon_gate_open()
        def dungeon_gate_open():
            wm.change_tile((13,0),'k')
            wm.wormhole((13,0),"dungeon level 1",(14,1))
        if mhc.quest_is_done("dungeon gate open"):
            dungeon_gate_open()
        else:
            wm.add_enter_event((13,1),lambda: finish_dungeon_gate_quest())
        wm.wormhole((16,0),"tower level 1",(2,1))
        
        wm.add_decoration((15,7), "crystal ball")
        wm.add_enter_event((15,7), look_into_crystal_ball)

#####################################################################
# Tower level 1                                                     #
#####################################################################
class World_tower_level1:
    def __init__(self, wm, ui, mhc):
        wm.wormhole((3,0),"castle",(17,1))
        wm.wormhole((6,0),"tower level 2",(2,1))
        for (x,y) in wm.random_clear_tiles(0.2,range(1,9),range(2,9)):
            wm.add_enemy((x,y),'tower',choice(tower_enemies),['kanaword',('kanji',200)],1)


#####################################################################
# Tower level 2                                                     #
#####################################################################
class World_tower_level2:
    def __init__(self, wm, ui, mhc):
        wm.wormhole((3, 0), "tower level 1", (7, 1))
        wm.wormhole((6, 0), "tower level 3", (2, 1))
        for (x,y) in wm.random_clear_tiles(0.2, range(1, 9),range(2, 9)):
            wm.add_enemy((x, y), 'tower', choice(tower_enemies), ['kanaword', ('kanji', 200)], 1)
#####################################################################
# Tower level 3                                                     #
#####################################################################
class World_tower_level3:
    def __init__(self, wm, ui, mhc):
        wm.wormhole((3,0),"tower level 2", (7,1))
        wm.wormhole((4,5),"icy mountains",(3,4))
        wm.add_decoration((3,4),"magical symbol R")
        wm.add_decoration((5,4),"magical symbol G")
        wm.add_decoration((2,5),"magical symbol Y")
        wm.add_decoration((6,5),"magical symbol R")
        wm.add_decoration((3,6),"magical symbol G")
        wm.add_decoration((5,6),"magical symbol Y")
        wm.add_decoration((4,5),"magical symbol Y")
        star  = [[False for y in range(10)] for x in range(10)]
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
        #                 ui.render_item(ui.map_viewport, (x*32,y*32), star[x][y])
        #                 if random() < 0.04:
        #                     star[x][y] = None
        #             else:
        #                 if random() < 0.002:
        #                     star[x][y] = choice(stars)
        # self.shader = lambda: ice_temple_shader()


#####################################################################
# Dungeon level 1                                                   #
#####################################################################
class World_dungeon_level1:
    def __init__(self, wm, ui, mhc):
        def dungeon_level_1_treasure(number, loc):
            quest_id = "treasure %d" % number
            def grab_treasure():
                mhc.quest_do(quest_id)
                for i in range(1,7):
                    if not mhc.quest_is_done("treasure %s" % i):
                        ui.change_text([U"You retrieved one of the treasure chests"])
                        return
                mhc.quest_do("dungeon level 2 open")
                ui.change_text([
                    U"You retrieved the last treasure chest on this level.",
                    U"The next level is open."
                ])
                dungeon_level_2_open()
            if not mhc.quest_is_done(quest_id):
                wm.add_item(loc, "chest 1", grab_treasure)
        
        for (x,y) in wm.random_clear_tiles(0.15,range(1,39),range(1,39)):
            wm.add_enemy((x,y),'dungeon',choice(dungeon_lvl_1_enemies),[('kanji',450)],2)
        for (x,y) in wm.random_clear_tiles(0.01,range(1,39),range(1,39)):
            wm.add_item((x,y),"copper coins", lambda: mhc.receive_money(1))
        for (x,y) in wm.random_clear_tiles(0.1,range(1,39),range(1,39)):
            wm.add_decoration((x,y),choice(dungeon_lvl_1_decorations))

        wm.wormhole((15, 0), "castle", (12, 1))

        def dungeon_level_2_open():
            wm.change_tile((35, 13), '<')
            wm.wormhole((35, 13), "dungeon level 2", (15, 1))
        if mhc.quest_is_done("dungeon level 2 open"):
            dungeon_level_2_open()

        dungeon_level_1_treasure(1, (11, 14))
        dungeon_level_1_treasure(2, (38, 13))
        dungeon_level_1_treasure(3, (1, 22))
        dungeon_level_1_treasure(4, (17, 24))
        dungeon_level_1_treasure(5, (4, 38))
        dungeon_level_1_treasure(6, (28, 36))


#####################################################################
# Dungeon level 2                                                   #
#####################################################################
class World_dungeon_level2:
    def __init__(self, wm, ui, mhc):
        def dungeon_level_2_treasure(number, loc):
            quest_id = "treasure %d" % number
            def grab_treasure():
                mhc.quest_do(quest_id)
                for i in range(7,15):
                    if not mhc.quest_is_done("treasure %s" % i):
                        ui.change_text([U"You retrieved one of the treasure chests"])
                        return
                mhc.quest_do("dungeon level 3 open")
                ui.change_text([
                    U"You retrieved the last treasure chest on this level.",
                    U"The next level is open."
                ])
                dungeon_level_3_open()
            if not mhc.quest_is_done(quest_id):
                wm.add_item(loc, "chest 2", grab_treasure)

        dungeon_level_2_treasure(7, (18, 2))
        dungeon_level_2_treasure(8, (14, 24))
        dungeon_level_2_treasure(9, (22, 32))
        dungeon_level_2_treasure(10, (36, 18))
        dungeon_level_2_treasure(11, (38, 24))
        dungeon_level_2_treasure(12, (38, 37))
        dungeon_level_2_treasure(13, (5, 17))
        dungeon_level_2_treasure(14, (1, 38))

        wm.wormhole((15, 0), "dungeon level 1", (35, 12))

        def dungeon_level_3_open():
            wm.change_tile((7, 24), '<')
            wm.wormhole((7, 24), "dungeon level 3", (15,1))
        if mhc.quest_is_done("dungeon level 3 open"):
            dungeon_level_3_open()

        for (x, y) in wm.random_clear_tiles(0.15, range(1, 39),range(1, 39)):
            wm.add_enemy((x, y), 'dungeon', choice(dungeon_lvl_2_enemies), [('kanji', 600)], 3)
        for (x, y) in wm.random_clear_tiles(0.01, range(1, 39), range(1, 39)):
            wm.add_item((x, y), "copper coins", lambda: mhc.receive_money(1))
        for (x,y) in wm.random_clear_tiles(0.1, range(1, 39), range(1, 39)):
            wm.add_decoration((x, y), choice(dungeon_lvl_2_decorations))

#####################################################################
# Dungeon level 3                                                   #
#####################################################################
class World_dungeon_level3:
    def __init__(self, wm, ui, mhc):
        def dungeon_level_3_treasure(number, loc):
            quest_id = "treasure %d" % number
            def grab_treasure():
                mhc.quest_do(quest_id)
                for i in range(14,21):
                    if not mhc.quest_is_done("treasure %s" % i):
                        ui.change_text([U"You retrieved one of the treasure chests"])
                        return
                mhc.quest_do("dungeon finished")
                ui.change_text([
                    U"Congratulations.",
                    U"You retrieved the last treasure chest in the dungeon.",
                ])
            if not mhc.quest_is_done(quest_id):
                wm.add_item(loc, "chest 4", grab_treasure)

        dungeon_level_3_treasure(15, (13, 1))
        dungeon_level_3_treasure(16, (12, 16))
        dungeon_level_3_treasure(17, (36, 2))
        dungeon_level_3_treasure(18, (26, 34))
        dungeon_level_3_treasure(19, (16, 38))
        dungeon_level_3_treasure(20, (1, 16))

        wm.wormhole((15, 0), "dungeon level 2", (7, 23))

        for (x, y) in wm.random_clear_tiles(0.15, range(1, 39), range(1, 39)):
            wm.add_enemy((x, y), 'dungeon',choice(dungeon_lvl_3_enemies), [('kanji', 900)], 3)
        for (x, y) in wm.random_clear_tiles(0.02, range(1, 39),range(1, 39)):
            if randint(0, 2) == 0:
                wm.add_item((x, y), "silver coins", lambda: mhc.receive_money(2))
            else:
                wm.add_item((x, y), "copper coins", lambda: mhc.receive_money(1))
        for (x, y) in wm.random_clear_tiles(0.1, range(1, 39), range(1, 39)):
            wm.add_decoration((x, y), choice(dungeon_lvl_3_decorations))

