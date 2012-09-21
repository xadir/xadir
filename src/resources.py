import pygame
from pygame.locals import *
from config import *

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
	if rect.width % width or rect.height % height:
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

