#!/usr/bin/python

import sys
import pygame
from random import *
pygame.init()

font_path = "/usr/share/fonts/truetype/kochi/kochi-gothic.ttf"

size     = width, height = 640, 480
screen   = pygame.display.set_mode(size, pygame.DOUBLEBUF)
font     = pygame.font.Font(font_path, 18)
font_big = pygame.font.Font(font_path, 64)
clock    = pygame.time.Clock()
color    = (128, 255, 128)
color_eph = (255, 128, 255)

txt = [
("今日", "きょう"),
("日", "に"),
("本", "ほん"),
("語", "ご"),
("を", None),
("勉", "べん"),
("強", "きょう"),
# ("勉強", "べんきょう"),
("しよう", None),
("強", "きょう"),
("調", "ちょう"),
# ("強調", "きょうちょう"),
]

txt = [
("月", "げつ", False),
("曜", "よう", True),
("日", "び", False),
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
    screen.fill((0, 0, 0))

    x = 32
    for i in range(len(txt)):
        (b, f, kf) = txt[i]
        b_r = font_big.render(b, True, color)
        screen.blit(b_r, (x, 64))
        (w, h) = (b_r.get_width(), b_r.get_height())
        if f:
            if kf: f_r = font.render(f, True, color)
            else:  f_r = font.render(f, True, color_eph)
            (fw, fh) = (f_r.get_width(), f_r.get_height())
            screen.blit(f_r, (x-fw/2+w/2, 64-fh))
        x = x + w

    pygame.display.flip()
    clock.tick(50)
