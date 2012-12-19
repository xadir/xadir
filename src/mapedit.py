import os, sys, time
import pygame
from pygame.locals import *
from resources import *
from config import *
from grid import *
from bgmap import *
from UI import *
import eztext

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
		size = max(size[0], 4), size[1] + 1

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

		self.maplist_container = UIContainer(None, (957, 500), (238, 400), self.screen)
		self.save_input = eztext.Input(x=self.maplist_container.x + 10, y=self.maplist_container.y + 100, maxlength=40, color=COLOR_FONT, prompt='Map name: ')

		self.save_btn = FuncButton(self.maplist_container, 10, 150, 218, 30, [["Save map", None]], None, ICON_FONTSIZE, self.screen, 1, (self.do_save, None), True, False, True)

		self.buttons = []
		self.maplist = []

		self.maplist_container.spritegroup.add(self.save_btn)
		self.buttons.append(self.save_btn)

		self._update_ui_elements()

		if mapname:
			self.load(mapname)

	def _update_ui_elements(self):
		# XXX: naming is all screwed up now :P
		self.right = UIGrid(0, 0, self.grid, TILE_SIZE, 0)
		self.spawnui = UIGrid(self.right.width + 6, 0, self.spawntools, TILE_SIZE, 1)
		self.left = UIGrid(self.right.width + 6, self.spawnui.height + 6, self.tools, OVERLAY_SIZE, 1)
		#self.load_btn = UIComponent(self.right.width + 6, self.left.y + self.left.height + 6, self.left.width, 50)
		#self.save_btn = UIComponent(self.right.width + 6, self.left.y + self.left.height + 6, self.left.width, 50)
		self.done_btn = UIComponent(self.right.width + 6, self. left.y + self.left.height + 6, self.left.width, 50)

	def list_maps(self):
		maps = os.listdir(MAPDIR)
		print maps
		return maps

	def add_map(self, mapname, x, y, w, h):
		map_btn = FuncButton(self.maplist_container, x, y, w, h, [[mapname, None]], None, 20, self.screen, 1, (self.select_map, mapname), True, False, True)
		print mapname, map_btn, w, h
		self.maplist_container.spritegroup.add(map_btn)
		self.buttons.append(map_btn)

	def update_maplist(self):
		maps = self.list_maps()
		i = 0
		while i < len(maps):
			if maps[i] == "tools.txt" or maps[i] == "README":
				maps.pop(i)
				i = i - 1
			else:
				try:
					map, mapsize, spawns = load_map(maps[i])
					for row in map:
						for tile in row:
							assert tile in self.tiles
				except:
					maps.pop(i)
					i = i - 1
				i = i + 1
		x = 10
		y = 10
		w = 218
		h = 20
		margin = 5
		self.maplist = []
		for m in maps:
			self.maplist.append(self.add_map(m, x, y, w, h))
			y = (y + h) + margin

	def select_map(self, mapname):
		self.mapname = mapname
		print self.mapname
		self.load(self.mapname)
		self.save_input.value = self.mapname

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
		with file(path, 'wb') as f:
			self._save(f)
		# XXX: Figure out which error rename() raises on Windows when the file already exists
		#try:
		#os.rename(path + '.new', path)
		#except xxx:
		#	os.(path + '.old')
		#	os.rename(h, path + '.old')
		#	os.rename(path + '.new', path)
		#	os.remove(path + '.old')
		# XXX: should we leave the old map in path.old?

	def draw(self):
		
		self.maplist_container.draw()

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

		for btn, text in [(self.save_btn, 'Save map'), (self.done_btn, 'Back to main menu')]:
			self.screen.fill((127, 127, 127), (btn.x, btn.y, btn.width, btn.height))
			text = self.spawnfont.render(text, True, (0, 0, 0))
			rect = text.get_rect()
			rect.center = (btn.x + btn.width / 2, btn.y + btn.height / 2)
			self.screen.blit(text, rect)

	def do_load(self):
		print 'Load'

	def do_save(self, xxx):
		self.save(self.save_input.value)

	def do_done(self):
		self.done = True

	def click(self, event):
		for b in self.buttons:
			if b.contains(*event.pos):
				f = b.function[0]
				f(b.function[1])
				break

	def loop(self):
		self.update_maplist()
		left, right, spawnui = self.left, self.right, self.spawnui

		btns = [
			(self.save_btn, 'save', self.do_save),
			#(self.load_btn, 'load', self.do_load),
			(self.done_btn, 'done', self.do_done),
		]

		area = None
		start = None
		tool = None

		self.done = False
		while not self.done:
			events = pygame.event.get()
			self.screen.fill((0, 0, 0))

			self.draw()
			self.save_input.update(events)
			self.save_input.draw(self.screen)

			pygame.display.flip()

			for event in events:
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						self.click(event)
						if left.contains(*event.pos):
							area = 'left'
						elif right.contains(*event.pos):
							area = 'right'
						elif spawnui.contains(*event.pos):
							area = 'spawn'
						#else:
						#	for btn, name, func in btns:
						#		if btn.contains(*event.pos):
						#			area = name
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
						#for btn, name, func in btns:
						#	if area == name and btn.contains(*event.pos):
						#		func()
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

