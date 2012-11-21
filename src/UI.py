"""""""""""""""""""""""""""""""""
@name: UI-Class
@author: Heikki Juva

@description:
Contains all the UI-components
used in Xadir.
"""""""""""""""""""""""""""""""""

import sys, time
import pygame
from resources import *

class UIComponent:
	def __init__(self, x, y, width, height):
		self.x = x
		self.y = y
		self.width = width
		self.height = height

	def contains(self, x, y):
		return x >= self.x and y >= self.y and x < self.x + self.width and y < self.y + self.height

	def translate(self, x, y):
		return x - self.x, y - self.y
		
class Tile(pygame.sprite.Sprite):
	def __init__(self, image, rect=None, layer=0):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = image.get_rect()
		self._layer = layer
		if rect is not None:
			self.rect = rect

class Func_Button(UIComponent):
	def __init__(self, x, y, width, height, border, bg_color, border_color, text, image, fontsize, surface, function, enabled=True):
		UIComponent.__init__(self, x, y, width, height)
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.border = border
		self.enabled = enabled
		self.function = function
		self.surface = surface
		self.fontsize = fontsize
		self.bg_color = bg_color
		self.border_color = border_color
		self.images = image
		self.rects = []
		
		self.rects.append(self.add_round_rect(pygame.Rect(self.x, self.y, self.width + (self.border * 2), self.height + (self.border * 2)), border_color))
		self.rects.append(self.add_round_rect(pygame.Rect(self.x + self.border, self.y + self.border, self.width, self.height), bg_color))
		
		self.texts = []
		if text != None:
			for t in text:
				self.add_text(t[0], t[1], self.fontsize)

	def add_text(self, string, coords, fontsize):
		font = pygame.font.Font(FONT, int(fontsize*FONTSCALE))
		text = font.render(string, True, (0, 0, 0), self.bg_color)
		rect = text.get_rect()
		if coords != None:
			rect.x = self.x + coords[0]
			rect.y = self.y + coords[1]
		else:
			rect.centerx = self.x + (self.width/2)
			rect.centery = self.y + (self.height/2)
		self.texts.append([text, rect])

	def get_function(self):
		return self.function
		
	def enable(self):
		self.enabled = True
	
	def disable(self):
		self.enabled = False
		
	def add_round_rect(self, rect, color, radius=0.4):

		"""
		AAfilledRoundedRect(surface,rect,color,radius=0.4)

		surface : destination
		rect    : rectangle
		color   : rgb or rgba
		radius  : 0 <= radius <= 1
		"""

		rect         = Rect(rect)
		color        = Color(*color)
		alpha        = color.a
		color.a      = 0
		pos          = rect.topleft
		rect.topleft = 0,0
		rectangle    = pygame.Surface(rect.size,SRCALPHA)

		circle       = pygame.Surface([min(rect.size)*3]*2,SRCALPHA)
		pygame.draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
		circle       = pygame.transform.smoothscale(circle,[int(min(rect.size)*radius)]*2)

		radius              = rectangle.blit(circle,(0,0))
		radius.bottomright  = rect.bottomright
		rectangle.blit(circle,radius)
		radius.topright     = rect.topright
		rectangle.blit(circle,radius)
		radius.bottomleft   = rect.bottomleft
		rectangle.blit(circle,radius)

		rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
		rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

		rectangle.fill(color,special_flags=BLEND_RGBA_MAX)
		rectangle.fill((255,255,255,alpha),special_flags=BLEND_RGBA_MIN)

		return [rectangle, pos]
	
	def toggle_visibility(self):
		if self.enabled: self.enabled = False
		else: self.enabled = True

	def draw(self):
		for r in self.rects:
			self.surface.blit(r[0], r[1])
		if self.images != None:
			for i in self.images:
				rect = i[0].get_rect()
				rect.x = self.x + i[1][0]
				rect.y = self.y + i[1][1]
				self.surface.blit(i[0], rect)
		for t in self.texts:
			self.surface.blit(t[0], t[1])