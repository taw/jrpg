# -*- coding: UTF-8 -*-

from random import choice, random

library_decorations = [
    "spellbook gray 1",
    "spellbook gray 2",
    "spellbook gray 3",
    "spellbook gray 4",
    "spellbook blue 1",
    "spellbook blue 2",
    "spellbook blue 3",
    "spellbook blue 4",
    "spellbook green 1",
    "spellbook green 2",
    "spellbook green 3",
    "spellbook green 4",
    "spellbook red 1",
    "spellbook red 2",
    "spellbook red 3",
    "spellbook red 4",
    "spellbook cyan 1",
    "spellbook cyan 2",
    "spellbook cyan 3",
    "spellbook cyan 4",
    "spellbook pink 1",
    "spellbook pink 2",
    "spellbook pink 3",
    "spellbook pink 4",
]

wizard_decorations = [
    "spellbook blue 1",
    "spellbook blue 2",
    "spellbook blue 3",
    "spellbook blue 4",
    "spellbook blue 5",
    "spellbook blue 6",
    "spellbook blue 7",
    "spellbook blue 8",
    "spellbook blue 9",
    "spellbook green 1",
    "spellbook green 2",
    "spellbook green :w5",
    "spellbook green 4",
    "spellbook green 5",
    "spellbook green 6",
    "spellbook green 7",
    "spellbook green 8",
    "spellbook green 9",
    "spellbook red 1",
    "spellbook red 2",
    "spellbook red 3",
    "spellbook red 4",
    "spellbook red 5",
    "spellbook red 6",
    "spellbook red 7",
    "spellbook red 8",
    "spellbook red 9",
    "potion 1",
    "potion 2",
    "potion 3",
    "potion 4",
    "potion 5",
    "potion 6",
    "potion 7",
    "potion 8",
    "potion 9",
    "potion 10",
    "potion 11",
    "potion 12",
    "potion 13",
    "potion 14",
    "potion 15",
    "potion 16",
    "potion 17",
    "potion 18",
    "potion 19",
    "potion 20",
    "potion 21",
    "potion 22",
    "potion 23",
    "potion 24",
    "potion 25",
    "potion 26",
]

cave_enemies = [
    "bat 1",
    "bat 2",
    "bat 3",
    "bat 4",
    "bat 5",
    "skeleton 1",
    "skeleton 2",
    "skeleton 3",
    "skeleton 4",
    "skeleton 5",
    "skeleton 6",
    "skeleton 7",
]


class World_library:
    def __init__(self, wm, ui, mhc):
        wm.wormhole((5, 9), "world", (33, 35))
        # monk1
        wm.add_chara("elf-monk",
                     route=[(1, 1), (1, 3), (4, 3), (4, 1)],
                     event=lambda: ui.change_text([
                         U"You get more experienced as you defeat\
                                 the kanji monsters.",
                         U"But you must look for new monsters all the time,",
                         U"as each can give you experience at most 3 times.",
                         U"And you can only get some if you win in a \
                                 good style.",
                     ]))
        # monk2
        wm.add_chara("elf-monk",
                     route=[(5, 1), (5, 3), (8, 3), (8, 1)],
                     event=lambda: ui.change_text([
                          U"The first time you meet a demon, you may see\
                                its name.",
                          U"Later, you must remember it.",
                          U"If you don't want to start all over again, you\
                                 may save with F2,",
                          U"and load with F4. But it's a very\
                                 traumatic experience."
                    ]))

        # This monk is not really telling the true, he still thinks
        # it's an old version of jrpg ;-)
        # monk3
        wm.add_chara("elf-monk",
                     route=[(1, 4), (8, 4), (8, 6), (1, 6)],
                     event=lambda:  ui.change_text([
                         U"There are different demons in each location.",
                         U"So it would be too boring to stay for\
                                 too long in one place.",
                         U"If you're done with the demons around the town,",
                         U"maybe try the castle northwest."
        ]))
        for y in range(10):
            for x in range(10):
                if wm.current_map_get_element(x, y) == 'W':
                    wm.add_decoration((x, y), choice(library_decorations))


#####################################################################
# Hospital map                                                      #
#####################################################################
class World_hospital:
    def __init__(self, wm, ui, mhc):
        emergency_healing = (mhc.hp == 0)
        healed_today = [False]  # Just to get sane msgs

        def nurse_healing():
            if mhc.hp != mhc.hpmax:
                mhc.change_hp(mhc.hpmax)
                if emergency_healing:
                    ui.append_text([U"You're healed now.", U"Take care of yourself the next time."])
                else:
                    ui.change_text([U"You're healed now.", U"Take care of yourself the next time."])
                healed_today[0] = True
            elif not healed_today[0]:
                ui.change_text([U"Come here if you're hurt.", U"The hospital can cure your wounds."])

        wm.wormhole((5, 9), "world", (2, 37))
        wm.add_chara("nurse", route=[(1, 5), (8, 5)], event=nurse_healing)

        # Automatic nurse_healing() if entered almost-dead
        # (mostly for teleports after lost battles)
        if emergency_healing:
            nurse_healing()


#####################################################################
# Wizard shop                                                       #
#####################################################################
class World_wizard_shop:
    def __init__(self, wm, ui, mhc):
        just_given_potion = [False]
        def wizard_quests():
            if not mhc.quest_is_done("antiheat potion idea"):
                ui.change_text([U"I'm making potions from mushrooms.", U"But you don't seem to need any."])
            elif not (mhc.quest_is_done("antiheat potion yellow") and mhc.quest_is_done("antiheat potion bgreen")):
                mhc.quest_do("antiheat potion recipe")
                ui.change_text([
                    U"Oh, you need an anti-heat potion",
                    U"Bring me some yellow and bright green mushrooms."])
            elif not mhc.quest_is_done("antiheat potion complete"):
                mhc.loss_item("yellow mushroom")
                mhc.loss_item("green mushroom 2")
                mhc.gain_item("potion 5")
                mhc.quest_do("antiheat potion complete")
                ui.change_text([U"Here's your potion.", U"Enjoy the desert."])
                just_given_potion[0] = True
            elif not just_given_potion[0]:
                ui.change_text([
                    U"I'm making potions from mushrooms.",
                    U"But you don't seem to need any more potions for now."])
        def setup_decorations(x,y):
            wm.add_decoration((x,y),choice(wizard_decorations))
        wm.wormhole((5, 9), "world", (38, 35))
        wm.add_chara("wizard-gray",route=[(3,4),(6,4)],event=wizard_quests)
        for y in range(1,3):
            for x in range(1,9):
                if random() < 0.6:
                    setup_decorations(x, y)
        for y in range(3, 9):
            if random() < 0.9:
                setup_decorations(1, y)
                setup_decorations(8, y)


#####################################################################
# Angel sanctuary                                                   #
#####################################################################
class World_angel_sanctury:
    def __init__(self, wm, ui, mhc):
        def angel_quest():
            if mhc.quest_is_done("reward for level 3"):
                ui.change_text([U"I am guardian angel of\
                        software development.",
                                U"I'm impressed\
                                        that you finished all quests in jrpg.",
                                U"Please send your savefile to its developer,",
                                U"and he is sure to add some new areas ^_^"])
            else:
                ui.change_text([U"I am guardian angel of\
                        software development.",
                                U"If you actually finish all quests in jrpg,",
                                U"send the savefile to its developer,",
                                U"and he is sure to add some new areas."])

        wm.wormhole((3, 0), "world", (35, 36))

        wm.add_chara("angel-blue",
                     route=[(3, 2), (6, 2), (7, 3), (7, 6), (6, 7),
                            (3, 7), (2, 6), (2, 3)],
                     event=angel_quest)


#####################################################################
# Blacksmith                                                        #
#####################################################################
class World_blacksmith:
    def __init__(self, wm, ui, mhc):
        def blacksmith_quest():
            if mhc.quest_is_done("magic sword complete"):
                ui.change_text([U"Good monster hunting with\
                        your awesome magic sword"])
            elif mhc.quest_is_done("blue crystals complete"):
                mhc.loss_item("sword")
                mhc.loss_item("blue crystals")
                mhc.gain_item("magic sword")
                mhc.quest_do("magic sword complete")
            elif mhc.quest_is_done("sword complete"):
                ui.change_text([U"This was once a legendary sword,\
                        but its enchantments wore off",
                                U"Find some magic blue\
                                        crystals in a cave to the East",
                                U"And I'll reenchant it"])
            elif mhc.quest_is_done("broken sword complete"):
                mhc.loss_item("broken sword")
                mhc.gain_item("sword")
                mhc.quest_do("sword complete")
                ui.change_text([U"Here, I fixed your sword!",
                                U"This was once a legendary sword,\
                                        but its enchantments wore off",
                                U"Find some magic blue crystals\
                                        in a cave to the East",
                                U"And I'll reenchant it"])
            else:
                ui.change_text([U"You look like a hero, but you have no sword",
                                U"There's one on a meadow to the south.",
                                U"It's broken but if you bring\
                                        it here I'll fix it for you"])

        wm.wormhole((3, 0), "world", (41, 36))

        wm.add_chara("dwarf-smith",
                     route=[(4, 3), (5, 3), (6, 4), (6, 5), (5, 6),
                            (4, 6), (3, 5), (3, 4)],
                     event=blacksmith_quest)

        wm.add_decoration((1, 6), "pickaxe")
        wm.add_decoration((8, 5), "hammer")
        wm.add_decoration((8, 7), "pickaxe")
        wm.add_decoration((4, 8), "pickaxe")
        wm.add_decoration((6, 8), "hammer")
        wm.add_decoration((3, 8), "hammer")


#####################################################################
# Cave                                                              #
#####################################################################
class World_cave:
    def __init__(self, wm, ui, mhc):
        def blue_crystals():
            mhc.gain_item("blue crystals")
            mhc.quest_do("blue crystals complete")
            ui.change_text([U"Now take the blue crystal back to the smith"])

        wm.wormhole((0, 7), "world", (60, 37))
        if mhc.quest_is_done("sword complete") and\
                not mhc.quest_is_done("blue crystals complete"):
            wm.add_item((27, 2), "blue crystals", blue_crystals)
        for (x, y) in wm.random_clear_tiles(0.2, range(2, 29), range(2, 14)):
            wm.add_enemy((x, y), 'dungeon', choice(cave_enemies),
                         ['kanaword', ('kanji', 100)], 1)
