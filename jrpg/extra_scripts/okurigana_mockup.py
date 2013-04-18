#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys, pygame
from math import sqrt,floor
from random import *
pygame.init()

font_path = "/usr/share/fonts/truetype/kochi/kochi-gothic.ttf"

size     = width, height = 640, 480
screen   = pygame.display.set_mode(size, pygame.DOUBLEBUF)
font     = pygame.font.Font(font_path, 18)
font_big = pygame.font.Font(font_path, 64)
clock    = pygame.time.Clock()
color    = (128, 255, 128)
color_eph= (255, 128, 255)

txt = [
(u"今日", u"きょう"),
(u"日", u"に"),
(u"本", u"ほん"),
(u"語", u"ご"),
(u"を", None),
(u"勉", u"べん"),
(u"強", u"きょう"),
#(u"勉強", u"べんきょう"),
(u"しよう", None),
(u"強", u"きょう"),
(u"調", u"ちょう"),
#(u"強調", u"きょうちょう"),
]

txt = [
(u"月", u"げつ", False),
(u"曜", u"よう", True),
(u"日", u"び", False),
]

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
    screen.fill((0,0,0))
    
    x = 32
    for i in range(len(txt)):
        (b,f,kf)=txt[i]
        b_r = font_big.render(b, True, color)
        screen.blit(b_r, (x,64))
        (w,h) = (b_r.get_width(), b_r.get_height())
        if f:
            if kf: f_r = font.render(f, True, color)
            else:  f_r = font.render(f, True, color_eph)
            (fw,fh) = (f_r.get_width(), f_r.get_height())
            screen.blit(f_r, (x-fw/2+w/2,64-fh))
        x = x + w

    pygame.display.flip()
    clock.tick(50)
