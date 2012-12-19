import os, sys, time
import pygame
from pygame.locals import *
from resources import *
from config import *
from grid import *
from bgmap import *

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
	def __init__(self, screen, mapname=None):
		self.screen = screen
		self.width, self.height = self.screen.get_size()

		self.spawnfont = pygame.font.Font(None, 20)

		tools, size, _ = load_map('tools.txt')

		# Ensure toolbar has empty squares too (aka. removal tool)
		# Ensure at least same width than spawnpoint toolbox
		size = max(size[0], 6), max(size[1], self.height/17)

		self.res = Resources(None)
		self.res.load_terrain()
		self.res.terrain[None] = [pygame.Surface(TILE_SIZE)]
		self.tiles = {}
		for name, image in self.res.terrain.iteritems():
			image = image[0]#.copy()
			new_image = pygame.Surface(OVERLAY_SIZE)
			#new_image.fill((127, 127, 127))
			#image.set_alpha(127)
			#new_image.blit(image, (0, OVERLAY_SIZE[1] - 2*TILE_SIZE[1]))
			image.set_alpha(255)
			new_image.blit(image, (0, OVERLAY_SIZE[1] - TILE_SIZE[1]))
			self.tiles[name] = new_image
		self.tiles['F'].blit(self.res.overlay['F-m'], (0, 0))

		self.grid = BackgroundMap(None, 20, 15, self.res)
		self.spawns = Grid(20, 15)
		self.tools = Grid(*size)
		self.spawntools = Grid(4, 2, [[1, 2, 3, 4], [5, 6, None, None]])

		for y, row in enumerate(tools):
			for x, tile_name in enumerate(row):
				self.tools[x, y] = tile_name

		# XXX: add tools that arent specified in toolfile

		self.sprites = pygame.sprite.LayeredUpdates()
		self.sprites.add(self.grid.sprites.values())

		self._update_ui_elements()

		if mapname:
			self.load(mapname)

	def _update_ui_elements(self):
		# XXX: naming is all screwed up now :P
		self.right = UIGrid(0, 0, self.grid, TILE_SIZE, 0)
		self.spawnui = UIGrid(self.right.width + 6, 0, self.spawntools, TILE_SIZE, 1)
		self.left = UIGrid(self.right.width + 6, self.spawnui.height + 6, self.tools, OVERLAY_SIZE, 1)

	def _load(self, mapname):
		map, mapsize, spawns = load_map(mapname)
		assert mapsize[0] <= 20 and mapsize[1] <= 15

		self.sprites.remove(self.grid.sprites.values())
		self.grid = BackgroundMap(map, 20, 15, self.res)
		self.sprites.add(self.grid.sprites.values())

		self.spawns = Grid(20, 15)
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
				print >>f, self.grid[x, y] or '?',
			print >>f

	def load(self, mapname):
		self.mapname = mapname
		self._load(mapname)
		self._update_ui_elements()

	def save(self, mapname):
		path = os.path.join(MAPDIR, mapname)
		with file(path + '.new', 'wb') as f:
			self._save(f)
		# XXX: Figure out which error rename() raises on Windows when the file already exists
		#try:
		os.rename(path + '.new', path)
		#except xxx:
		#	os.remove(path + '.old')
		#	os.rename(path, path + '.old')
		#	os.rename(path + '.new', path)
		#	os.remove(path + '.old')
		# XXX: should we leave the old map in path.old?

	def draw(self):
		for (x, y), num in self.spawntools.items():
			if num:
				text = self.spawnfont.render(str(num), True, (255, 255, 255))
				rect = text.get_rect()
				rx, ry = self.spawnui.grid2screen_translate(x, y)
				rect.center = (rx + self.spawnui.cell_size[0]/2, ry + self.spawnui.cell_size[1]/2)
				self.screen.blit(text, rect)

		self.screen.fill((63, 63, 63), pygame.Rect(self.right.width + 1, self.spawnui.height + 1, self.left.width + 5, 4))

		for (x, y), tile in self.tools.items():
			if tile:
				self.screen.blit(self.tiles[tile], self.left.grid2screen_translate(x, y))

		self.screen.fill((63, 63, 63), pygame.Rect(self.right.width + 1, 0, 4, 720))

		self.sprites.update()
		self.sprites.draw(self.screen)

		for (x, y), num in self.spawns.items():
			if num:
				text = self.spawnfont.render(str(num), True, (255, 255, 255))
				rect = text.get_rect()
				rx, ry = self.right.grid2screen_translate(x, y)
				rect.center = (rx + self.right.cell_size[0]/2, ry + self.right.cell_size[1]/2)
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
				elif event.type == pygame.QUIT:
					self._save(sys.stdout)
					sys.exit()

			time.sleep(0.05)

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
		UIComponent.__init__(self, x, y, grid.width * (cell_size[0] + border_width) - border_width, grid.height * (cell_size[1] + border_width) - border_width)
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

	screen = init_pygame()
	win = MapEditor(screen, mapname)
	win.loop()

