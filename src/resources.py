import pygame
from pygame.locals import *
from config import *

def init_pygame():
	pygame.mixer.pre_init(48000)
	pygame.init()
	screen = pygame.display.set_mode((1200, 720))
	return screen

def load_image(name, colorkey=None, scale=1):
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
	if scale is not 1:
		image_rect = image.get_rect()
		image = pygame.transform.scale(image, (image_rect.right*scale, image_rect.bottom*scale))
	return image

def load_tiles(name, (width, height), colorkey=None, scale=1):
	#print "Scaling: %d" % (scale)
	image = load_image(name, colorkey, scale)
	return parse_tiles(image, (width, height))

def parse_tiles(tileimage, (width, height)):
	rect = tileimage.get_rect()
	if rect.width % width or rect.height % height:
		print 'Tile image should be divisible to (%d,%d)' % (width, height)
	cols = rect.width / width
	rows = rect.height / height
	#print "parse_tiles - got %dx%d tileset with %d cols and %d rows" % (rect.width, rect.height, cols, rows)
	images = []
	for y in range(rows):
		row = []
		for x in range(cols):
			image = tileimage.subsurface((x*width, y*height, width, height))
			row.append(image)
		images.append(row)
	return images

def load_named_tiles(name, (width, height), colorkey=None, scale=1):
	images = load_tiles(name + '.png', (width, height), colorkey, scale)
	tiles = {}
	with file(os.path.join(GFXDIR, name + '.txt'), 'rb') as f:
		for y, line in enumerate(f):
			for x, name in enumerate(line.split()):
				tiles[name] = images[y][x]
	return tiles

def load_map(name):
	path = os.path.join(MAPDIR, name)
	with file(path, 'rb') as f:
		aliases = {}
		width = height = 0
		spawns = {}
		for line in f:
			cmd = line.strip().split()
			if not cmd:
				break
			if cmd[0] == 'SIZE':
				width, height = int(cmd[1]), int(cmd[2])
			elif cmd[0] == 'ALIAS':
				aliases[cmd[1]] = cmd[2]
			elif cmd[0] == 'SPAWN':
				spawns.setdefault(int(cmd[1]), []).append((int(cmd[2]), int(cmd[3])))
			else:
				raise ValueError, 'Unknown map directive'
		result = []
		for y in range(height):
			line = f.next()
			tiles = [aliases.get(tile, tile) for tile in line.split()]
			assert len(tiles) == width
			result.append(tiles)
	return result, (width, height), spawns

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

