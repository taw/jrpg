# -*- coding: UTF-8 -*-

from random import choice, random

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

class World_outside:
    def __init__(self, wm, ui, mhc):
        ###############################
        # WORMHOLES                   #
        ###############################
        wm.wormhole((7,8),"castle",(4,8))
        wm.wormhole((33,34), "library", (5,8))
        wm.wormhole((38,34), "wizard shop", (5,8))
        wm.wormhole((35,37), "angel sanctuary", (5,1))
        wm.wormhole((41,37), "blacksmith", (5,1))
        wm.wormhole((2,36),"hospital",(5,8)) # Hospital wormhole

        ###############################
        # CASTLE SOLDIERS AND EVENTS  #
        ###############################
        # The castle has many soldiers
        wm.add_chara("soldier-axe",route=[(9,15),(1,15),(1,16),(2,16),(2,10),(2,16),(1,16),(1,15)])
        wm.add_chara("soldier-axe",route=[(9,10),(9,13),(4,13),(4,10)])
        wm.add_chara("soldier-axe",route=[(18,15),(18,16),(17,16),(17,10),(17,16),(18,16),(18,15),(10,15)])
        wm.add_chara("soldier-axe",route=[(10,10),(10,13),(15,13),(15,10)])

        wm.add_chara("soldier-axe",route=[(2,1),(2,9),(2,1),(1,1),(1,2),(9,2),(1,2),(1,1)])
        # The building blocks this route, but it still works:
        wm.add_chara("soldier-axe",route=[(4,4),(9,4),(9,9),(4,9)])
        wm.add_chara("soldier-axe",route=[(17,1),(17,9),(17,1),(18,1),(18,2),(10,2),(18,2),(18,1)])
        # The building blocks this route, but it still works:
        wm.add_chara("soldier-axe",route=[(15,9),(15,4),(10,4),(10,9)])

        def open_castle_gate():
            if mhc.quest_is_done("castle gate open"): return
            ui.change_text([U"Oh, you're a hero. Please come in."])
            wm.change_tile((6,16),'k')
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
            wm.change_tile((6,16),'k')
        else:
            wm.add_enter_event((6,17), lambda: castle_gate_checkup())
        ###############################
        # ELVEN GATE                  #
        ###############################
        def open_elven_gate():
            wm.change_tile((23,36),'k')
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
        wm.add_chara("soldier-elf",route=[(22,35),(22,38)], event=elven_gate_soldier_event)
        if mhc.quest_is_done("elven gate tax"): open_elven_gate()
        wm.add_chara("soldier-elf",route=[(26,32),(26,37),(26,32),(23,31)])
        ###############################
        # ELVEN BRIDGE                #
        ###############################
        # There used to be a level test
        # but now it's just a nice way to skip useless kana part
        def open_bridge():
            wm.change_tile((46,31),'.')
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
        wm.add_chara("soldier-elf",route=[(45,32),(47,32)],event=bridge_soldier_event)
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
        wm.add_chara("arab-trader",route=[(44,13),(46,13)], event=arab_trader_quest)

        ###############################
        # ELVEN TRADER                #
        ###############################
        wm.add_chara("elf-trader",route=[(3,23), (3,24)], event=lambda: ui.change_text([
                U"Many animals and people have been possessed by kanji demons.",
                U"You may kill the demons by shouting their names.",
                U"I would do that myself, but there are too many names to remember.",
                U"Maybe you should visit the Elven town, it's south east from here."]))

        ###############################
        # FOREST 1                    #
        ###############################
        for (x,y) in wm.random_clear_tiles(0.1,range(0,10),range(40,50)):
            wm.add_enemy((x,y),'forest',choice(forest_enemies),['hiragana'],1)
        for (x,y) in wm.random_clear_tiles(0.05,range(10,30),range(40,50)):
            wm.add_enemy((x,y),'forest',choice(forest_enemies),['hiragana'],1)
        wm.add_item((1,41),"copper coins", lambda: mhc.receive_money(1))
        wm.add_item((1,45),"copper coins", lambda: mhc.receive_money(1))
        ###############################
        # DWARVEN HILLS               #
        ###############################
        for (x,y) in wm.random_clear_tiles(0.1,range(30,50),range(40,60)):
            wm.add_enemy((x,y),'hills',choice(mountain_enemies),['hiragana','katakana'],1)
        for (x,y) in wm.random_clear_tiles(0.02,range(30,50),range(40,60)):
            wm.add_item((x,y),"copper coins", lambda: mhc.receive_money(1))

        ###############################
        # MEADOW                      #
        ###############################
        def meadow_quest():
            ui.change_text([U"You've found the magic sword but it's broken."])
            mhc.gain_item("broken sword")
            mhc.quest_do("broken sword complete")
        if not mhc.quest_is_done("broken sword complete"):
            wm.add_item((21,56),"broken sword", meadow_quest)

        ###############################
        # CAVE ENTRANCE               #
        ###############################
        wm.wormhole((61,37),"cave",(1,7))

        ###############################
        # FOREST 2                    #
        ###############################
        def add_random_forest_mushrooms(x,y):
            rmush = choice(mushroom_forest_decoration_mushrooms)
            if mhc.quest_is_done("antiheat potion recipe"):
                if rmush == "yellow mushroom" and not mhc.quest_is_done("antiheat potion yellow"):
                    item = wm.add_item((x,y), rmush)
                    wm.add_item_event(item, lambda: get_mushroom_yellow(item))
                elif rmush == "green mushroom 2" and not mhc.quest_is_done("antiheat potion bgreen"):
                    item = wm.add_item((x,y), rmush)
                    wm.add_item_event(item, lambda: get_mushroom_bgreen(item))
                else:
                    wm.add_decoration((x,y),rmush)
            else:
                wm.add_decoration((x,y),rmush)
        def get_mushroom_yellow(item):
            if not mhc.quest_is_done("antiheat potion yellow"):
                # Already got some other mushrooms of the same type
                wm.remove_item(item)
                mhc.gain_item("yellow mushroom")
                mhc.quest_do("antiheat potion yellow")
                ui.change_text([
                    U"You've got yellow mushrooms.",
                    U"You need yellow and bright green mushrooms for the potion."])
        def get_mushroom_bgreen(item):
            if not mhc.quest_is_done("antiheat potion bgreen"):
                # Already got some other mushrooms of the same type
                wm.remove_item(item)
                mhc.gain_item("green mushroom 2")
                mhc.quest_do("antiheat potion bgreen")
                ui.change_text([
                    U"You've got bright green mushrooms.",
                    U"You need yellow and bright green mushrooms for the potion."])
        for (x,y) in wm.random_clear_tiles(0.1,range(20,40),range(10,30)):
            wm.add_enemy((x,y),'marsh',choice(forest_enemies),['hiragana','katakana','kanaword'],1)
        # FIXME: new mushrooms will grow only if you leave the forest
        # To make it less annoying, let's double number of mushrooms
        for (x,y) in wm.random_clear_tiles(0.1,range(20,40),range(10,30)):
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
            wm.add_item((61,11),"spellbook blue 9",desert_quest)
        # Desert enemies
        for (x,y) in wm.random_clear_tiles(0.1,range(50,60),range(10,20)):
            wm.add_enemy((x,y),'desert',choice(desert_enemies),['kanaword',('kanji',100)],1)
        for (x,y) in wm.random_clear_tiles(0.2,range(50,70),range(20,30)):
            wm.add_enemy((x,y),'desert',choice(desert_enemies),['kanaword',('kanji',100)],1)
        for (x,y) in wm.random_clear_tiles(0.2,range(60,70),range(10,20)):
            wm.add_enemy((x,y),'desert',choice(desert_enemies),['kanaword',('kanji',100)],1)
        # Desert decorations
        wm.add_decoration((57,23),"skeleton 3")
        wm.add_decoration((55,11),"bones")
        wm.add_decoration((51,17),"skull")
        wm.add_decoration((63,16),"skull")
        wm.add_decoration((65,14),"skeleton 5")
        wm.add_decoration((61,24),"skeleton 1")
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
                    wm.add_enter_event((x,y),lambda:desert_heat())

class World_icy_mountains:
    def __init__(self, wm, ui, mhc):
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
        wm.wormhole((3,3),"tower level 3",(4,4))
        # Add decorations
        wm.add_decoration((2,2),"magical symbol R")
        wm.add_decoration((4,2),"magical symbol G")
        wm.add_decoration((1,3),"magical symbol Y")
        wm.add_decoration((5,3),"magical symbol R")
        wm.add_decoration((2,4),"magical symbol G")
        wm.add_decoration((4,4),"magical symbol Y")
        wm.add_decoration((3,3),"magical symbol Y")

        ###############################
        # ICY MOUNTAINS               #
        ###############################
        for (x,y) in wm.random_clear_tiles(0.2,range(10,20),range(0,10)):
            wm.add_enemy((x,y),"ice",choice(ice_enemies),[('kanji',300)],1)
        for (x,y) in wm.random_clear_tiles(0.2,range(0,20),range(10,20)):
            wm.add_enemy((x,y),"ice",choice(ice_enemies),[('kanji',300)],1)
        for (x,y) in wm.random_clear_tiles(0.3,range(20,50),range(0,20)):
            wm.add_enemy((x,y),"ice",choice(ice_enemies),[('kanji',300)],1)
        def ice_quest():
            ui.change_text([U"You've got a red spellbook."])
            mhc.gain_item("spellbook red 9")
            mhc.quest_do("ice artifact")
        if not mhc.quest_is_done("ice artifact"):
            wm.add_item((45,6),"spellbook red 9",ice_quest)
