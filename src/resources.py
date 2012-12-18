import pygame
from pygame.locals import *
from config import *
import time

class Resources:
	def __init__(self, screen):
		self.screen = screen

	def load_terrain(self):
		self.terrain = load_named_tiles('tilemap_terrain', TILE_SIZE, (255, 0, 255), SCALE)
		self.terrain = {'G': [self.terrain['G']], 'D': [self.terrain['D']], 'F': [self.terrain['G']], 'W': [self.terrain['W[1]'], self.terrain['W[2]']]}
		self.borders = load_named_tiles('tilemap_borders', BORDER_SIZE, (255, 0, 255), SCALE)
		self.overlay = load_named_tiles('tilemap_overlay', OVERLAY_SIZE, (255, 0, 255), SCALE)

	def load_races(self):
		raceimages = load_tiles('races.png', CHAR_SIZE, (255, 0, 255), SCALE)
		racenames = file(os.path.join(GFXDIR, 'races.txt')).read().split('\n')

		self.races = {}
		for name, images in zip(racenames, raceimages):
			self.races[name] = {270: images[0], 180: images[1], 0: images[2], 90: images[3]}

	def load_selections(self):
		self.selections = {}
		for name, color in [('red', (255, 0, 0)), ('green', (10, 212, 0))]:
			surf = pygame.Surface(TILE_SIZE)
			surf.fill(color)
			surf.set_alpha(120)
			self.selections[name] = surf

def init_pygame():
	pygame.mixer.pre_init(48000)
	pygame.init()
	screen = pygame.display.set_mode((1200, 720))
	pygame.mixer.set_reserved(1)
	return screen

def change_sound(channel, new_sound, fade_ms, loops = -1):
	if channel.get_sound():
		channel.set_endevent(USEREVENT)
		channel.fadeout(fade_ms)
		while pygame.event.wait().type != USEREVENT:
			pass
		channel.set_endevent()
	channel.play(new_sound, loops = loops, fade_ms = fade_ms)

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

