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
Pygame scrolling surface 
"""
import pygame
from pygame.locals import *

# from scrollsurface_config import * # Constants defining colours and Scrolling Speeds
class Msg_view(pygame.Surface):
	def __init__(self, width, height , dx = 5, dy = 5):
		super(Msg_view, self).__init__( (width, height) )
		self.scroll_x = 0
		self.scroll_y = 0
		self.dx = dx
		self.dy = dy
		self.rect = pygame.Rect(0, 0, 1, 1)
		self.set_rect((0,0), width , height)

	def set_rect(self, xy, w, h):
	        self.rect.topleft = xy
	        self.size = w, h
    
	def set_text(self, string, colour, x, y, font = "", fontsize = 32):
		self.string = str(string)
		pygame.font.init()
		if font == "":
			font = pygame.font.get_default_font()
		font_renderer = pygame.font.Font(font, fontsize)
		self.label = font_renderer.render( string, 1, colour )
		self.set_rect( ( self.label.get_bounding_rect().width, self.get_rect().height ), x, y )
		# Render label at the correct position
		
	def draw_text(self,surface):
		surface.blit(self.label, ( (self.get_rect().left + self.scroll_x), (self.get_rect().top + self.scroll_y) ) )
		rect = self.label.get_rect(x=self.get_rect().left + self.scroll_x, y=self.get_rect().top + self.scroll_y)
		# pygame.draw.rect(surface, pygame.Color('red'), rect, 1)

# scrollfunctions for Msg_view
	def scrollleft(self, surface):
		self.scroll_x += self.dx
		if self.scroll_x >= 0:
		# stop scrolling at the right edge of the label
			self.scroll_x = 0
		surface.scroll(-1 * self.dx, 0)

	def scrollright(self, surface):
		self.scroll_x -= self.dx
		fm_rect = self.label.get_rect(x = self.scroll_x, y = self.scroll_y )
		to_rect = surface.get_rect()
		if fm_rect.right < to_rect.right:
			self.scroll_x = to_rect.right - fm_rect.w - 10
		surface.scroll(self.dx, 0)
	
	def scrollup(self, surface):
		self.scroll_y -= self.dy
		if self.scroll_y <= 0:
			self.scroll_y = 0
		surface.scroll(0, -1 * self.dy)
	
	def scrolldown(self, surface):	
		self.scroll_y += self.dy
		height_difference = surface.get_height() - self.label.get_height()
		if self.scroll_y >= height_difference -self.dy:
			self.scroll_y = height_difference -self.dy
		surface.scroll(0, self.dy)
