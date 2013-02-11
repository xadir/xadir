import os, sys, time
import pygame
from pygame.locals import *
from resources import *
from UI import *

from tiles import *
from pixelfont import *

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

class MessageWin:
	def __init__(self, screen, text, color = (0, 255, 0)):
		self.screen = screen
		self.width, self.height = self.screen.get_size()

		self.background = pygame.Surface((self.width, self.height))
		self.background.fill((0, 0, 0))

		self.fps = 30
		self.clock = pygame.time.Clock()

		self.res = Resources(None)

		self.sprites = pygame.sprite.LayeredDirty(_time_threshold = 1000.0)
		self.sprites.set_clip()

		image = draw_pixel_text(text, 2*SCALE, color)
		rect = image.get_rect()
		rect.center = (self.width/2, self.height/2)
		self.sprites.add(StaticSprite(image, rect, 0))

	def draw(self, frames = 1):
		for i in range(frames):
			self.clock.tick(self.fps)
			self.sprites.update()
			self.sprites.clear(self.screen, self.background)
			# Update layers
			self.sprites._spritelist.sort(key = lambda sprite: sprite._layer)
			self.sprites.draw(self.screen)
			pygame.display.flip()

	def loop(self):
		self.done = False
		while not self.done:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.done = True

			self.draw()

if __name__ == "__main__":
	screen = init_pygame()

	win = Window()
	win.loop()

