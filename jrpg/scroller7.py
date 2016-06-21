#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  c6_graphics_2.py
#  
#  Copyright 2016 Jorrit Linnert <jorrit@jorpandy>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
"""
Pygame demo for Msg_view scrollable surface
"""
import pygame
from msg_view import *
from pygame.locals import *
from scrollsurface_config import * # Constants defining colours and Scrolling Speeds

dx = dy = 1
pygame.init()

# Set width and height of screen and define surfaces
size = (800, 480)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("My Game")
msg = screen.subsurface( (0,320), (800,160) )		

# ----------- MAIN program --------------------
msg_viewport = Msg_view(800, 160, X_DELTA, Y_DELTA)
xymonitor = Msg_view(100,00)

msg_clip = Rect((0, 0), (800, 160))
msg.set_clip(msg_clip)
msg.fill(GREEN)
msg_viewport.set_text("Dit is een flink lange tekst die illustreert dat je soms scrolling nodig hebt", BLACK, 0,10)

# disable mouse cursor
pygame.mouse.set_visible(0)

# loop until user clicks [Close]
done = False

# manage screen update frequency
clock = pygame.time.Clock()

#---------- Main Program Loop -------
while not done:

# ----- Main Event Loop -----

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			done = True
		elif event.type == pygame.KEYDOWN:
			if event.key == KEY_QUIT:
				done = True 
			elif event.key == KEY_SCR_LEFT:     # (A)
				msg_viewport.scrollleft(msg_viewport)
			elif event.key == KEY_SCR_RIGHT:      # (B)
				msg_viewport.scrollright(msg_viewport)
			elif event.key == KEY_SCR_UP:   # (Y)
				msg_viewport.scrollup(msg_viewport)
			elif event.key == KEY_SCR_DOWN: # (X)
				msg_viewport.scrolldown(msg_viewport)

# ------ Game Logic --------

# ------ Drawing Code ------
# First, clear screen to white,
	screen.fill(WHITE)
	msg.fill(GREEN)
# Draw repeating lines
	beginx = 100
	for x in range (1, 30):
		x_positie = beginx + x * 10
		pygame.draw.line(screen, RED, (x_positie, 0) , (x_positie, 100), 2)

# Draw rect
	blokje = (200 ,20 ,50 ,50)
	pygame.draw.rect(screen, BLACK, blokje)
# Draw a green line that is 5 pixels wide
	pygame.draw.line(screen, GREEN, [0, 0], [100, 1000], 5)

	scrollvalues = str("scroll_x: "+str(msg_viewport.scroll_x)+" scroll_y: "+str(msg_viewport.scroll_y) + "   " + str(msg_viewport.label.get_width() ))
	xymonitor.set_text(scrollvalues, BLACK, 100, 100)
	xymonitor.draw_text(screen)
	msg_viewport.draw_text(msg)
# Don't put drawing commands below this or they will be erased
# ------  Display ----------
	pygame.display.flip()

# ------ Screen update frequency -------
	clock.tick(60)

# ------ close window and exit ---------
pygame.quit()	
