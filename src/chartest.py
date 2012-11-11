import sys, time
import pygame
from resources import *
from grid import *
from algo import *

SIZE = 15
COUNT = 10

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

class CharTest:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((600, 600))

		self.charfield = pygame.Surface((600, 600))
		self.charfield_rect = pygame.Rect(0, 0, 600, 600)
		self.charfield.fill((150,150,150))
		"""
		self.load_characters('sprite_collection.png')
		print self.charnames

		self.sprites = pygame.sprite.LayeredUpdates()
		tile = self.chartypes[self.charnames[0] + '_' + '270']
		self.sprites.add(Tile(tile, pygame.Rect(TILE_SIZE[0], TILE_SIZE[1], *TILE_SIZE), layer = 0))
		"""

		self.sprites = pygame.sprite.LayeredUpdates()
		self.sprites.add(race_sprite('longear').get_sprite(0, 0, '270'))
		self.sprites.add(race_sprite('longear').get_sprites(0, 60))


	def loop(self):

		while 1:
			self.screen.fill((127, 127, 127))
			self.sprites.draw(self.screen)
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

			time.sleep(0.05)

class race_sprite:
	def load_characters(self, filename):
		#chars1 = load_tiles('sprite_collection.png', CHAR_SIZE, (255, 0, 255), SCALE)
		#chars2 = load_tiles('sprite_collection_2.png', CHAR_SIZE, (255, 0, 255), SCALE)
		
		chars = load_tiles(filename, CHAR_SIZE, (255, 0, 255), SCALE)

		self.charnames = []
		self.chartypes = {}
		for i, char in enumerate(chars):
			name = 'char' + str(i+1)
			self.charnames.append(name)
			self.chartypes[name + '_270'] = char[0]
			self.chartypes[name + '_180'] = char[1]
			self.chartypes[name + '_0'] = char[2]
			self.chartypes[name + '_90'] = char[3]
	
	def __init__(self, race):
		self.race = race
		self.sprites = pygame.sprite.LayeredUpdates()
		races = {'longear': ['sprite_collection.png', 'char1']}

		temp = races[race]
		self.path = temp[0]
		self.place = temp[1]

		self.load_characters(self.path)

	def get_sprites(self, x=0, y=0):
		self.sprites = pygame.sprite.LayeredUpdates()
		tiles = [self.chartypes[self.place + '_' + str(0)] , self.chartypes[self.place + '_' + str(90)], self.chartypes[self.place + '_' + str(180)], self.chartypes[self.place + '_' + str(270)]]
		for i in range(len(tiles)):
			self.sprites.add(Tile(tiles[i], pygame.Rect(x+(48*i)+TILE_SIZE[0], y+TILE_SIZE[1], *TILE_SIZE), layer = 0))
		return self.sprites

	def get_sprite(self, x=0, y=0, orientation=270):
		self.sprites = pygame.sprite.LayeredUpdates()
		self.sprites.add(Tile(self.chartypes[self.place + '_' + str(orientation)], pygame.Rect(x+TILE_SIZE[0], y+TILE_SIZE[1], *TILE_SIZE), layer = 0))
		return self.sprites


class Tile(pygame.sprite.Sprite):
	def __init__(self, image, rect=None, layer=0):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = image.get_rect()
		self._layer = layer
		if rect is not None:
			self.rect = rect

if __name__ == "__main__":
	win = CharTest()
	win.loop()

