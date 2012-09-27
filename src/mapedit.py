import os, sys, time
import pygame
from pygame.locals import *
from resources import *
from config import *
from grid import *

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

TL, TR, BR, BL = range(4)
def parse_tile(s):
	if s is None:
		return [None, None, None, None, None]
	tl, tr, br, bl, n = s
	return [tl, tr, br, bl, n]

class MapEditor:
	def __init__(self, width=640, height=480):
		pygame.init()
		self.width = width
		self.height = height
		self.screen = pygame.display.set_mode((self.width, self.height))

		self.tiles = load_named_tiles('placeholder_tilemap', (16, 16), (255, 0, 255))
		tools, size, _ = load_map('tools.txt')

		self.grid = Grid(24, 14)
		self.tools = Grid(9, 29)

		for y, row in enumerate(tools):
			for x, tile_name in enumerate(row):
				self.tools[x, y] = tile_name

		# XXX: add tools that arent specified in toolfile

	def draw(self):
		for (x, y), tile in self.tools.items():
			if tile:
				self.screen.blit(self.tiles[tile], (x * 17, y * 17))

		self.screen.fill((63, 63, 63), pygame.Rect(154, 0, 4, 480))

		for (x, y), tile in self.grid.items():
			if tile:
				self.screen.blit(self.tiles[tile], (160 + x * 17, y * 17))

	def loop(self):
		left = UIComponent(0, 0, 160, 480)
		right = UIComponent(160, 0, 480, 480)

		area = None
		start = None
		tool = None
		while 1:
			self.screen.fill((0, 0, 0))
			self.draw()
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						if left.contains(*event.pos):
							area = 'left'
						elif right.contains(*event.pos):
							area = 'right'
						start = event.pos
					else:
						if right.contains(*event.pos):
							x, y = right.translate(*event.pos)
							x, y = x/17, y/17
							inpaint(self.grid, self.tiles.keys(), (x, y))
				elif event.type == pygame.MOUSEBUTTONUP:
					if event.button == 1:
						if area == 'left' and left.contains(*event.pos):
							x, y = left.translate(*event.pos)
							x, y = x/17, y/17
							tool = self.tools[x, y]
						if area == 'right' and right.contains(*event.pos):
							x, y = right.translate(*event.pos)
							x, y = x/17, y/17
							try:
								self.grid[x, y] = tool
							except:
								pass
						area = None
						start = None
				elif event.type == pygame.MOUSEMOTION:
					if area == 'right' and right.contains(*event.pos):
						x, y = right.translate(*event.pos)
						x, y = x/17, y/17
						try:
							self.grid[x, y] = tool
						except:
							print "You went outside the borders"
				elif event.type == pygame.KEYUP:
					if event.key == pygame.K_SPACE:
						for pos, value in self.grid.items():
							if value is not None:
								continue
							inpaint(self.grid, self.tiles.keys(), pos)
				elif event.type == pygame.QUIT:
					print 'SIZE', self.grid.width, self.grid.height
					print
					for y in range(self.grid.height):
						for x in range(self.grid.width):
							print self.grid[x, y] or '?????',
						print
					sys.exit()

			time.sleep(0.05)

def inpaint(grid, tile_names, pos):
	items = list(grid.env_values(pos, 1))
	if len(items) != 9:
		return
	items = map(parse_tile, items)
	tl = list(set([items[3][TR], items[0][BR], items[1][BL]]) - set([None]))
	tr = list(set([items[1][BR], items[2][BL], items[5][TL]]) - set([None]))
	bl = list(set([items[3][BR], items[6][TR], items[7][TL]]) - set([None]))
	br = list(set([items[7][TR], items[8][TL], items[5][BL]]) - set([None]))
	tl = tl[0] if len(tl) == 1 else None
	tr = tr[0] if len(tr) == 1 else None
	bl = bl[0] if len(bl) == 1 else None
	br = br[0] if len(br) == 1 else None
	matches = set()
	for name in tile_names:
		ttl, ttr, tbr, tbl = parse_tile(name)[:4]
		if tl in (ttl, None) and tr in (ttr, None) and bl in (tbl, None) and br in (tbr, None):
			matches.add(ttl + ttr + tbr + tbl)
	if len(matches) == 1:
		try:
			tn = list(set(item[-1] for item in items if item[-1] is not None))[0]
		except IndexError:
			tn = '1'
		grid[pos] = list(matches)[0] + tn

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

if __name__ == "__main__":
	#if len(sys.argv) < 2:
	#	print 'syntax: %s FILE' % (sys.argv[0], )
	#	sys.exit()

	win = MapEditor()
	win.loop()

