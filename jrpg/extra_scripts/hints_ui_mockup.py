#!/usr/bin/python
# -*- coding: UTF-8 -*-

font_path = "/usr/share/fonts/truetype/kochi/kochi-gothic.ttf"

import sys, pygame, pickle, re
from math import floor

pygame.display.init()
pygame.font.init()

###########################################################
# This class manages the common part of the UI            #
###########################################################
class UI:
    def __init__(self):
        self.clock    = pygame.time.Clock()
        size = width, height = 640, 480
        #self.screen   = pygame.display.set_mode(size, pygame.DOUBLEBUF|pygame.FULLSCREEN)
        self.screen  = pygame.display.set_mode(size, pygame.DOUBLEBUF)
        self.font     = pygame.font.Font(font_path, 18)
        self.font_med = pygame.font.Font(font_path, 40)
        self.font_big = pygame.font.Font(font_path, 64)
        self.key = [False for i in range(512)]
    def tick(self):
        fpsLimit = 40
        time_so_far = self.clock.tick()
        time_max    = int(1000.0/fpsLimit)
        time_left   = time_max - time_so_far
        if time_left > 0:
            pygame.time.wait(time_left)
        #print time_left, self.clock.get_fps()
    def key_down(self, key):
        self.key[key] = True
    def key_up(self, key):
        self.key[key] = False
    def key_pressed(self, key):
        return(self.key[key])

    #####################################################################
    # Helper text-rendering function                                    #
    # anchor (0.0, 0.0) - loc is text's top left corner                 #
    # anchor (0.5, 0.5) - loc is text's center                          #
    # anchor (1.0, 1.0) - loc is text's bottom right corner             #
    # row_spacing - *total* distance between rows (not only whitespace) #
    #####################################################################
    def render_text_unicolor(self, font, text, loc, anchor, color, row_spacing=0):
        text = [(t,color) for t in text]
        self.render_text_multicolor(font, text, loc, anchor, row_spacing)
    def render_text_multicolor(self, font, text, loc, anchor, row_spacing):
        for i in range(len(text)):
            (t,color) = text[i]
            text_r = font.render(t, True, color)
            (x,y)   = loc
            (w,h)   = (text_r.get_width(), text_r.get_height())
            (ax,ay) = anchor
            fin_loc = (floor(x-ax*w),floor(y+i*row_spacing-ay*h))
            self.screen.blit(text_r, fin_loc)
    def render_furi(self,furicode,xy,font_main,font_furi,color_base,color_furi):
        (x,y) = xy
        for i in range(len(furicode)):
            (base,furi) = furicode[i]
            base_r = font_main.render(base, True, color_base)
            self.screen.blit(base_r, (x,y))
            (w,h) = (base_r.get_width(), base_r.get_height())
            if furi:
                furi_r = font_furi.render(furi, True, color_furi)
                (fw,fh) = (furi_r.get_width(), furi_r.get_height())
                self.screen.blit(furi_r, (x-fw/2+w/2,y-fh))
            x = x + w
    def blit(self):
        color_kanji = (128, 255, 128)
        color_furi  = (255, 128, 255)

        color_kanji_related = (128, 192, 255)
        color_kanji_similar = (255, 128, 128)

        color_furi_related  = (192, 224, 255)
        color_furi_similar  = (255, 192, 192)

        self.screen.fill((0,0,0))

        main = [(u"～", None), (u"人", u"じん")]
        other_readings = [
            ([(u"人", u"にん")], u"person"),
            ([(u"人", u"ひと")], u"person"),
        ]
        meaning = [
            u"citizen of some nation"
        ]
        similar = [
            ([(u"入", u"にゅう")], u"to enter")
        ]
        related = [
            ([(u"～", None), (u'者', u'しゃ')], u"person of some specialization"),
#            ([(u"～", None), (u'生', u'せい')], u"person ergaging in educational activities"),
            ([(u"～", None), (u'手', u'しゅ')], u"person doing menial works"),
        ]

        self.render_furi(main,(32,32),self.font_big,self.font,color_kanji,color_furi)
        self.render_text_unicolor(self.font, meaning, (32+2*64+32,32), (0,0), color_furi, 32)

        line = 0
        for (k,m) in other_readings:
            y=32+64+32+line*70
            self.render_furi(k,(32,y),self.font_med,self.font,color_kanji,color_furi)
            self.render_text_unicolor(self.font, [m], (32+2*48+32,y), (0,0), color_furi, 32)
            line = line+1
        for (k,m) in related:
            y=32+64+32+line*70
            self.render_furi(k,(32,y),self.font_med,self.font,color_kanji_related,color_furi_related)
            self.render_text_unicolor(self.font, [m], (32+2*48+32,y), (0,0), color_furi_related, 32)
            line = line+1
        for (k,m) in similar:
            y = 32+64+32+line*70
            self.render_furi(k,(32,y),self.font_med,self.font,color_kanji_similar,color_furi_similar)
            self.render_text_unicolor(self.font, [m], (32+2*48+32,y), (0,0), color_furi_similar, 32)
            line = line+1

    def main_loop(self):
        while 1:
            # Check UI events
            for event in pygame.event.get():
	        if event.type == pygame.QUIT:
	            sys.exit()
	        elif event.type == pygame.KEYDOWN:
	            self.key_down(event.key)
	            if event.key == pygame.K_RETURN:
	        	pygame.display.toggle_fullscreen()
	            elif event.key == pygame.K_ESCAPE:
	        	sys.exit()
        	elif event.type == pygame.KEYUP:
        	    self.key_up(event.key)
            self.blit()
            pygame.display.flip()
            self.tick()
ui = UI()
ui.main_loop()
