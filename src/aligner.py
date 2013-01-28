import os, sys, time
import pygame
from pygame.locals import *
from resources import *
from grid import *
from UI import *

from race import races, Race
from armor import armors, Armor, default as default_armor
from hair import hairs
from charclass import classes, CharacterClass
from character import Character
from charsprite import CharacterSprite

from tiles import *
from pixelfont import *

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
		self.background.fill((127, 127, 127))

		self.fps = 30
		self.clock = pygame.time.Clock()

		self.res = Resources(None)
		self.res.load_races()
		self.res.load_hairs()

		self.sprites = pygame.sprite.LayeredDirty(_time_threshold = 1000.0)
		self.sprites.set_clip()

		grid = FakeGrid(CHAR_SIZE)
		class_ = classes.keys()[0]

		races_ = races.keys()
		raceses = [races_[:len(races_)/2], races_[len(races_)/2:]]
		self.chars = []
		for r, races_ in enumerate(raceses):
			for x, hair in enumerate(hairs):
				for y, race in enumerate(races_):
					pos = (1 + r * (len(hairs) + 1) + x, 1 + y)
					armor = None
					char = CharacterSprite(None, Character(None, race, class_, 0, 0, 0, 0, armor, None, hair), pos, 270, grid, self.res)
					self.sprites.add(char)
					self.chars.append(char)

		for x, (hairname, hair) in enumerate(hairs.items()):
			ht = HairXY(hair, (int((x + 1.5) * CHAR_SIZE[0]), 30))
			self.sprites.add(ht)

		for r, races_ in enumerate(raceses):
			for y, race in enumerate(races_):
				ht = HairL(races[race], ((r * (len(hairs) + 1) + 0.5) * CHAR_SIZE[0], (y + 1.5) * CHAR_SIZE[1]))
				self.sprites.add(ht)

		self.selected = None

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
		xhair = yhair = False

		self.done = False
		while not self.done:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.done = True
				if event.type == pygame.MOUSEBUTTONDOWN:
					grid_pos = event.pos[0] / CHAR_SIZE[0], event.pos[1] / CHAR_SIZE[1]
					if event.button in (1, 3):
						for char in self.chars:
							if char.grid_pos == grid_pos:
								self.selected = char
								break
						else:
							self.selected = None
					if event.button == 1:
						xhair = True
					if event.button == 3:
						yhair = True
					if event.button in (4, 5):
						delta = {4: -1, 5: 1}[event.button]
						if self.selected:
							if yhair:
								self.selected.hair.yoffset += delta
							elif xhair:
								self.selected.hair.xoffset += delta
							else:
								if self.selected.race.hairline is None:
									self.selected.race.hairline = 0
								self.selected.race.hairline += delta
				if event.type == pygame.MOUSEBUTTONUP:
					if event.button == 1:
						xhair = False
					if event.button == 3:
						yhair = False
				if event.type == pygame.KEYUP and event.key == K_SPACE:
					for char in self.chars:
						char.heading = (char.heading + 90) % 360

			self.draw()

class HairXY(StateTrackingSprite):
	def __init__(self, hair, center):
		StateTrackingSprite.__init__(self)
		self.hair = hair
		self.center = center

	def get_state(self):
		return self.hair.xoffset, self.hair.yoffset

	def redraw(self):
		self.image = draw_pixel_text(str(self.state), SCALE)
		self.rect = self.image.get_rect()
		self.rect.center = self.center

class HairL(StateTrackingSprite):
	def __init__(self, race, center):
		StateTrackingSprite.__init__(self)
		self.race = race
		self.center = center

	def get_state(self):
		return self.race.hairline

	def redraw(self):
		self.image = draw_pixel_text(str(self.state), SCALE)
		self.rect = self.image.get_rect()
		self.rect.center = self.center

if __name__ == "__main__":
	screen = init_pygame()

	win = Window(screen)
	win.loop()

