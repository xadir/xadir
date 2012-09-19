import os, sys, time
import pygame
from pygame.locals import *
from config import *

GFXDIR = os.path.join(BASEDIR, 'gfx')
SNDDIR = os.path.join(BASEDIR, 'snd')

def load_image(name, colorkey=None):
	path = os.path.join(GFXDIR, name)
	try:
		image = pygame.image.load(path)
	except pygame.error, message:
		print 'Cannot load image:', name
		raise SystemExit, message
	image = image.convert()
	if colorkey is not None:
		if colorkey is -1:
			colorkey = image.get_at((0,0))
		image.set_colorkey(colorkey, RLEACCEL)
	return image

def load_tiles(name, (width, height), colorkey=None):
	image = load_image(name, colorkey)
	return parse_tiles(image, (width, height))

def parse_tiles(tileimage, (width, height)):
	rect = tileimage.get_rect()
	if rect.width % width == 0 or rect.height % height == 0:
		print 'Tile image should be divisible to (%d,%d)' % (width, height)
	cols = rect.width / width
	rows = rect.height / height
	images = []
	for y in range(rows):
		row = []
		for x in range(cols):
			image = tileimage.subsurface((x*width, y*height, width, height))
			row.append(image)
		images.append(row)
	return images

def load_sound(name):
	class NoneSound:
		def play(self): pass
	if not pygame.mixer:
		return NoneSound()
	fullname = os.path.join(SNDDIR, name)
	try:
		sound = pygame.mixer.Sound(fullname)
	except pygame.error, message:
		print 'Cannot load sound:', wav
		raise SystemExit, message
	return sound

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

class PyManMain:
	"""Main class for init and creation of game."""

	def __init__(self, width=640, height=480):
		pygame.init()
		self.width = width
		self.height = height
		self.screen = pygame.display.set_mode((self.width, self.height))

	def MainLoop(self):
		self.LoadSprites();
		while 1:
			self.map_sprites.draw(self.screen)
			pygame.display.flip()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
			time.sleep(0.05)

	def LoadSprites(self):
		"""Load the sprites that we need"""
		self.map = Map([[0,0,0,0,0],[0,1,1,1,0],[0,0,1,0,0],[0,0,1,1,0]], 5, 4)
		self.map_sprites = self.map.getSprites()

class Map:
	"""Class for initialization of the map layer"""
	def __init__(self, map, height, width):
		self.sprite = []
		self.width = width
		self.height = height
		self.map = map
		self.map_sprites = pygame.sprite.Group()
		for x in range(self.width):
			for y in range(self.height):
				if map[x][y]:
					print "Water at: (" + str(x) + "," + str(y) + ")"
					self.map_sprites.add(Water(pygame.Rect(y*SIZE[1], x*SIZE[0], *SIZE)))
				else:
					print "Land at: (" + str(x) + "," + str(y) + ")"
					self.map_sprites.add(Land(pygame.Rect(y*SIZE[1], x*SIZE[0], *SIZE)))

	def getSprites(self):
		return self.map_sprites

class Land(pygame.sprite.Sprite):
	def __init__(self, rect=None):
		pygame.sprite.Sprite.__init__(self)
		self.image = lands[1][1]#load_image('land%d.jpg' % SIZE)
		self.rect = self.image.get_rect()
		if rect != None:
			self.rect = rect

class Water(pygame.sprite.Sprite):
	def __init__(self, rect=None):
		pygame.sprite.Sprite.__init__(self)
		self.image = waters[1][1]#load_image('water%d.jpg' % SIZE)
		self.rect = self.image.get_rect()
		if rect != None:
			self.rect = rect

SIZE = (16, 16)

if __name__ == "__main__":
	MainWindow = PyManMain()

	tiles = load_tiles('placeholder_tilemap.png', (48, 48))
	waters = parse_tiles(tiles[0][0], SIZE)
	lands = parse_tiles(tiles[0][1], SIZE)

	MainWindow.MainLoop()

