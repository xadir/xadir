import os, sys, time
import pygame
from pygame.locals import *
from resources import *
from grid import *
from UI import *

from race import races, Race
from armor import armors, Armor, default as default_armor
from charclass import classes, CharacterClass
from character import Character
from charsprite import CharacterSprite

from tiles import *

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

class FakeGrid:
	def __init__(self, size):
		self.x, self.y = (0, 0)
		self.cell_size = size

class Window:
	def __init__(self, screen):
		pygame.display.set_caption('Xadir')

		self.screen = screen
		self.width, self.height = self.screen.get_size()

		self.background = pygame.Surface((self.width, self.height))
		self.background.fill((0, 0, 0))

		self.fps = 30
		self.clock = pygame.time.Clock()

		self.res = Resources(None)
		self.res.load_races()

		self.sprites = pygame.sprite.LayeredDirty(_time_threshold = 1000.0)
		self.sprites.set_clip()

		grid = FakeGrid(CHAR_SIZE)
		class_ = classes.keys()[0]

		hairs = dict((char, None) for char in 'abcdefghij')
		races_ = races.keys()
		raceses = [races_[:len(races_)/2], races_[len(races_)/2:]]
		for r, races_ in enumerate(raceses):
			for x, hair in enumerate(hairs):
				for y, race in enumerate(races_):
					pos = (r * 10 + x, 1 + y)
					armor = None
					self.sprites.add(CharacterSprite(None, Character(None, race, class_, 0, 0, 0, 0, armor, None), pos, 270, grid, self.res))

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

	win = Window(screen)
	win.loop()

