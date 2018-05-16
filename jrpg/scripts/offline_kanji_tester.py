#!/usr/bin/python

from __future__ import print_function
import pygame, sys
import util

# This is just a simple script for scientific exploration
# of my kanji abilities ^_^

# Darn, we don't really need the hint engine, and it's there together with the book
import demonsoul
from random import *
from math import floor

# PUBD
import codecs
sys.stdin  = codecs.getwriter("utf-8")(sys.stdin)
sys.stdout = codecs.getwriter("utf-8")(sys.stdout)
sys.stderr = codecs.getwriter("utf-8")(sys.stderr)

util.init_pygame("JRPG")

class Model:
    def __init__(self):
        book = demonsoul.Book_of_demons()
        kanji_demons = book.demons[3]
        self.kanji_demons_with_ids = [(i, kanji_demons[i]) for i in range(len(kanji_demons))]
        # We want to test only the long term memory, but people also have short term memory
        # avoid short term memory interference
        self.seen_demons = {}
        self.select_a_new_demon()
    def select_a_new_demon(self):
        while True:
            demon_id, demon = choice(self.kanji_demons_with_ids)
            if not self.seen_demons.has_key(demon_id):
                self.seen_demons[demon_id] = True
                self.current_demon_id, self.current_demon = demon_id, demon.finalize()
                return
    def get_furicode(self):
        return self.current_demon.furicode()

class UI:
    def __init__(self):
        size = (640, 480)
        #self.screen = pygame.display.set_mode(size, pygame.DOUBLEBUF|pygame.FULLSCREEN)
        self.screen = pygame.display.set_mode(size, pygame.DOUBLEBUF)
        self.font, self.font_med, self.font_big = util.load_font(27, 60, 96)
        self.clock    = pygame.time.Clock()
        self.key = [False for i in range(512)]
        self.chara_buf = u""
    def render_kanji_name(self, furicode, (rel_x, rel_y), (anchor_x,anchor_y)):
        font_main  = self.font_big
        font_furi  = self.font
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
            #if furi and (keep_furi or not world.stats.xpctl.seen_soul(world.enemy_soul)):
            if furi and keep_furi:
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

        for (x, y, displayed_element) in displayed_elements:
            self.screen.blit(displayed_element, (rel_x+x+dx, rel_y+y+dy))
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
            #print(time_left, self.clock.get_fps())
        else: # Version for exact measurement - do not use :-)
            self.clock.tick()
            print(self.clock.get_fps())
    def main_loop(self):
        while True:
             # Check UI events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    ui.key_down(event.key)
                    # If any key was pressed, stop backspacing
                    # <backspace pressed> <a pressed> <backspace released> <a released>
                    #                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                    # The used probably meant to release backspace first and press a,
                    # but without this hack a would get backspaced too
                    if ui.key[pygame.K_BACKSPACE] and event.key != pygame.K_BACKSPACE:
                        ui.key_up(pygame.K_BACKSPACE)
                    if event.key == pygame.K_RETURN:
                        pygame.display.toggle_fullscreen()
                    elif event.key == pygame.K_ESCAPE:
                        sys.exit()
                    elif event.key == pygame.K_F12:
                        mhc.closeup()
                    elif event.key >= 97 and event.key <= 122: #'a'..'z'
                        self.chara_buf = self.chara_buf + chr(event.key)
                    elif event.key == 32: # space
                        self.chara_attack()
                    elif event.key == pygame.K_BACKSPACE:
                        self.bs_repeat = -1
                elif event.type == pygame.KEYUP:
                    ui.key_up(event.key)
            if ui.key[pygame.K_BACKSPACE]:
                if self.bs_repeat == -1: # Fresh
                    self.chara_buf = self.chara_buf[0:len(self.chara_buf)-1]
                    self.bs_repeat = 5
                if self.bs_repeat == 0:
                    self.chara_buf = self.chara_buf[0:len(self.chara_buf)-1]
                    self.bs_repeat = 2
                else:
                    self.bs_repeat = self.bs_repeat - 1
            self.render()
            ui.tick()
    def chara_attack(self):
        # Accidental keypress or sth like that
        if self.chara_buf == U"":
            return
        attack_ok = model.current_demon.answer_ok(self.chara_buf)
        print(model.current_demon_id, attack_ok, model.current_demon.xp_code(), self.chara_buf)
        model.select_a_new_demon()
        self.chara_buf = U""
    def key_down(self, key):
        self.key[key] = True
    def key_up(self, key):
        self.key[key] = False
    def key_pressed(self, key):
        return(self.key[key])
    def render(self):
        ui.screen.fill((0,0,0))
        furicode = model.get_furicode()
        ui.render_kanji_name(furicode, (320, 160), (0.0, 0.0))
        ui.render_text_unicolor(ui.screen, ui.font, [self.chara_buf],
                                (320, 320+80), (0.5, 0.5), (255, 128, 128))

ui = UI()
model = Model()

ui.main_loop()
