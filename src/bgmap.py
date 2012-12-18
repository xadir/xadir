import pygame

from config import *
from grid import Grid
from tiles import AnimatedTile

clamp = lambda v, minv, maxv: min(max(v, minv), maxv)
clamp_r = lambda v, minv, maxv: min(max(v, minv), maxv - 1)

class BackgroundMap(Grid):
	"""Map class to create the background layer, holds any static and dynamical elements in the field."""
	def __init__(self, map, width, height, res):
		Grid.__init__(self, width, height, map)
		self.terrain, self.borders, self.overlay = res.terrain, res.borders, res.overlay
		self.images = {}
		self.cell_size = TILE_SIZE
		self.x = self.y = 0
		self.sprites = Grid(width, height)
		for x, y in self.keys():
			tiles = self.get_real_tile((x, y))
			rect = tiles[0].get_rect()
			rect.top = y*TILE_SIZE[1] - (rect.height - TILE_SIZE[1])
			rect.left = x*TILE_SIZE[0]
			self.sprites[x, y] = AnimatedTile(tiles, rect, layer = L_MAP(y), interval = FPS / TILE_FPS)

	def get_repeated(self, (x, y)):
		return self[clamp_r(x, 0, self.width), clamp_r(y, 0, self.height)]

	def get_repeated_base(self, pos):
		tile = self.get_repeated(pos)
		if tile == 'F':
			return 'G'
		return tile

	def get_border(self, (x, y), side, tile):
		dirs = {'t': -1, 'b': 1, 'l': -1, 'r': 1, 'm': 0}
		hd, vd = dirs[side[1]], dirs[side[0]]
		d = (hd, vd)
		c = self.get_repeated_base((x + hd, y + vd)) != tile
		if 'm' in side:
			if c: return side.replace('m', ''), d
			return None, d
		h = self.get_repeated_base((x + hd, y)) != tile
		v = self.get_repeated_base((x, y + vd)) != tile
		if h and v: return '_'.join(side), d
		if h: return side[1], d
		if v: return side[0], d
		if c: return side, d
		return None, d

	def get_overlay(self, (x, y), tile):
		l = self.get_repeated((x - 1, y)) == tile
		r = self.get_repeated((x + 1, y)) == tile
		if l and r: return 'h'
		if l: return 'l'
		if r: return 'r'
		return 'm'

	def get_real_tile(self, pos):
		real_tile = tile = self[pos]
		if tile == 'F':
			tile = 'G'
		if tile in ('W', 'D'):
			borders = tuple(self.get_border(pos, side, tile) for side in 'tl tm tr ml mr bl bm br'.split())
		else:
			borders = ()
		name = (tile, borders)
		images = self.images.get(name)
		if not images:
			images = self.terrain[tile]
			if any(b for b, d in borders):
				orig_images = images
				images = []
				for image in orig_images:
					image = image.copy()
					for b, d in borders:
						if not b:
							continue
						border = self.borders[tile + '-' + b]
						image.blit(border, (((d[0] + 1) * BORDER_SIZE[0], (d[1] + 1) * BORDER_SIZE[1]), BORDER_SIZE))
					images.append(image)
				self.images[name] = images
		if real_tile == 'F':
			overlay_tile = real_tile + '-' + self.get_overlay(pos, real_tile)
			name = (tile, borders, overlay_tile)
			images2 = self.images.get(name)
			if not images2:
				orig_images = images
				images = []
				for orig_image in orig_images:
					image = pygame.Surface(OVERLAY_SIZE)
					image.fill((255, 0, 255))
					image.set_colorkey((255, 0, 255))
					image.blit(orig_image, ((0, OVERLAY_SIZE[1] - TILE_SIZE[1]), TILE_SIZE))
					overlay = self.overlay[overlay_tile]
					image.blit(overlay, ((0, 0), OVERLAY_SIZE))
					images.append(image)
				self.images[name] = images
			else:
				images = images2
		return images

