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
	def __init__(self, mapname=None, width=640, height=480):
		pygame.init()
		self.width = width
		self.height = height
		self.screen = pygame.display.set_mode((self.width, self.height))

		self.spawnfont = pygame.font.Font(None, 20)

		self.tiles = load_named_tiles('placeholder_tilemap', (16, 16), (255, 0, 255))
		tools, size, _ = load_map('tools.txt')

		# Ensure toolbar has empty squares too (aka. removal tool)
		# Ensure at least same width than spawnpoint toolbox
		size = max(size[0], 6), max(size[1], height/17)

		self.grid = Grid(20, 15)
		self.spawns = Grid(20, 15)
		self.tools = Grid(*size)

		if mapname:
			self._load(mapname)

		for y, row in enumerate(tools):
			for x, tile_name in enumerate(row):
				self.tools[x, y] = tile_name

		# XXX: add tools that arent specified in toolfile

		self.spawntools = Grid(6, 2, [range(1, 7), [None]*6])
		self.spawnui = UIGrid(0, 0, self.spawntools, (16, 16), 1)
		self.left = UIGrid(0, self.spawnui.height + 6, self.tools, (16, 16), 1)
		self.right = UIGrid(self.left.width + 6, 0, self.grid, (16, 16), 1)

	def _load(self, mapname):
		self.grid = Grid(20, 15)
		self.spawns = Grid(20, 15)

		map, mapsize, spawns = load_map(mapname)
		assert mapsize[0] <= 20 and mapsize[1] <= 15
		for y, row in enumerate(map):
			for x, col in enumerate(row):
				self.grid[x, y] = col
		for player_id, points in spawns.items():
			for point in points:
				self.spawns[point] = player_id

	def _save(self, f):
		print >>f, 'SIZE', self.grid.width, self.grid.height
		for (x, y), player_id in self.spawns.items():
			if player_id:
				print >>f, 'SPAWN', player_id, x, y
		print >>f
		for y in range(self.grid.height):
			for x in range(self.grid.width):
				print >>f, self.grid[x, y] or '?????',
			print >>f

	def draw(self):
		for (x, y), num in self.spawntools.items():
			if num:
				text = self.spawnfont.render(str(num), True, (255, 255, 255))
				rect = text.get_rect()
				rx, ry = self.spawnui.grid2screen_translate(x, y)
				rect.center = (rx + 8, ry + 8)
				self.screen.blit(text, rect)

		self.screen.fill((63, 63, 63), pygame.Rect(0, self.spawnui.height + 1, self.left.width + 1, 4))

		for (x, y), tile in self.tools.items():
			if tile:
				self.screen.blit(self.tiles[tile], self.left.grid2screen_translate(x, y))

		self.screen.fill((63, 63, 63), pygame.Rect(self.left.width + 1, 0, 4, 480))

		for (x, y), tile in self.grid.items():
			if tile:
				self.screen.blit(self.tiles[tile], self.right.grid2screen_translate(x, y))

		for (x, y), num in self.spawns.items():
			if num:
				text = self.spawnfont.render(str(num), True, (255, 255, 255))
				rect = text.get_rect()
				rx, ry = self.right.grid2screen_translate(x, y)
				rect.center = (rx + 8, ry + 8)
				self.screen.blit(text, rect)

	def loop(self):
		left, right, spawnui = self.left, self.right, self.spawnui

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
						elif spawnui.contains(*event.pos):
							area = 'spawn'
						start = event.pos
					else:
						if right.contains(*event.pos):
							x, y = right.screen2grid_translate(*event.pos)
							inpaint(self.grid, self.tiles.keys(), (x, y))
				elif event.type == pygame.MOUSEBUTTONUP:
					if event.button == 1:
						if area == 'left' and left.contains(*event.pos):
							x, y = left.screen2grid_translate(*event.pos)
							tool = ('tile', self.tools[x, y])
						if area == 'right' and right.contains(*event.pos):
							x, y = right.screen2grid_translate(*event.pos)
							if tool[0] == 'tile':
								self.grid[x, y] = tool[1]
							elif tool[0] == 'spawn':
								self.spawns[x, y] = tool[1]
						if area == 'spawn' and spawnui.contains(*event.pos):
							x, y = spawnui.screen2grid_translate(*event.pos)
							tool = ('spawn', self.spawntools[x, y])
						area = None
						start = None
				elif event.type == pygame.MOUSEMOTION:
					if area == 'right' and right.contains(*event.pos):
						x, y = right.screen2grid_translate(*event.pos)
						if tool[0] == 'tile':
							self.grid[x, y] = tool[1]
						elif tool[0] == 'spawn':
							self.spawns[x, y] = tool[1]
				elif event.type == pygame.KEYUP:
					if event.key == pygame.K_SPACE:
						for pos, value in self.grid.items():
							if value is not None:
								continue
							inpaint(self.grid, self.tiles.keys(), pos)
				elif event.type == pygame.QUIT:
					self._save(sys.stdout)
					sys.exit()

			time.sleep(0.05)

# XXX: try to do better - borders and holes remain unfilled atm
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

class UIGrid(UIComponent):
	def __init__(self, x, y, grid, cell_size, border_width = 0):
		UIComponent.__init__(self, x, y, grid.width * (cell_size[0] + border_width) - 1, grid.height * (cell_size[1] + border_width) - 1)
		self.grid = grid
		self.cell_size = cell_size
		self.border_width = border_width

	def screen2grid_translate(self, x, y):
		x, y = self.translate(x, y)
		return x / (self.cell_size[0] + self.border_width), y / (self.cell_size[1] + self.border_width)

	def grid2screen_translate(self, x, y):
		return self.x + x * (self.cell_size[0] + self.border_width), self.y + y * (self.cell_size[1] + self.border_width)

if __name__ == "__main__":
	mapname = None
	if len(sys.argv) >= 2:
		mapname = sys.argv[1]

	win = MapEditor(mapname)
	win.loop()

