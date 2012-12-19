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

class MapSelection:
	def __init__(self, screen, mapname=None, network=False, network_host=False):
		self.screen = screen
		self.width, self.height = self.screen.get_size()
		self.network = network
		self.network_host = network_host
		self.mapname = mapname

		self.spawnfont = pygame.font.Font(None, 20)

		self.ip_input_enabled = False
		self.port_input_enabled = False

		size = 4

		self.res = Resources(None)
		self.res.load_terrain()
		self.res.terrain[None] = [pygame.Surface(TILE_SIZE)]
		self.tiles = {}
		for name, image in self.res.terrain.iteritems():
			image = image[0]#.copy()
			new_image = pygame.Surface(OVERLAY_SIZE)
			image.set_alpha(255)
			new_image.blit(image, (0, OVERLAY_SIZE[1] - TILE_SIZE[1]))
			self.tiles[name] = new_image
		self.tiles['F'].blit(self.res.overlay['F-m'], (0, 0))

		self.grid = BackgroundMap(None, 20, 15, self.res)
		self.spawns = Grid(20, 15)

		self.sprites = pygame.sprite.LayeredUpdates()
		self.sprites.add(self.grid.sprites.values())

		self.sidebar_container = UIContainer(None, (957, 0), (238, 715), self.screen)

		self.ip_input = eztext.Input(x=self.sidebar_container.x + 16, y=12, maxlength=15, color=COLOR_FONT, prompt='IP: ')
		self.port_input = eztext.Input(x=self.sidebar_container.x + 16, y=78, maxlength=4, color=COLOR_FONT, prompt='Port: ')

		self.play_btn = FuncButton(self.sidebar_container, 10, 240, 218, 30, [["Play map", None]], None, ICON_FONTSIZE, self.screen, 1, (self.start_game, self.mapname), True, False, True)
		#if self.network_host:
		#	self.ip_btn = FuncButton(self.sidebar_container, 10, 10, 218, 30, [["127.0.0.1", None]], None, ICON_FONTSIZE, self.screen, 1, (self.select_field, "ip"), True, False, True)
		#else:
		self.ip_btn = FuncButton(self.sidebar_container, 10, 10, 218, 30, None, None, ICON_FONTSIZE, self.screen, 1, (self.select_field, "ip"), True, False, True)
		if network_host:
			self.ip_input.value += "127.0.0.1"
		self.port_btn = FuncButton(self.sidebar_container, 10, 75, 218, 30, None, None, ICON_FONTSIZE, self.screen, 1, (self.select_field, "port"), True, False, True)

		self.buttons = []
		self.maplist = []
		self.maplinks = []

		self.buttons.append(self.play_btn)
		if self.network:
			self.buttons.append(self.ip_btn)
			self.buttons.append(self.port_btn)

		self.sidebar_container.spritegroup.add(self.play_btn)
		if self.network:
			self.sidebar_container.spritegroup.add(self.ip_btn)
			self.sidebar_container.spritegroup.add(self.port_btn)

		if self.mapname:
			self.load(self.mapname)	
			

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

	def select_field(self, field):
		print "Clicked on field button"
		if field == "ip":
			if not self.network_host:
				print "Selected IP field"
				self.ip_input_enabled = True
				self.port_input_enabled = False
		if field == "port":
			print "Selected Port field"
			self.ip_input_enabled = False
			self.port_input_enabled = True

	def load(self, mapname):
		self.mapname = mapname
		self._load(mapname)

	def save(self, mapname):
		path = os.path.join(MAPDIR, mapname)
		with file(path + '.new', 'wb') as f:
			self._save(f)

	def draw(self):
		self.sprites.update()
		self.sprites.draw(self.screen)

		self.sidebar_container.draw()

		for (x, y), num in self.spawns.items():
			if num:
				text = self.spawnfont.render(str(num), True, (255, 255, 255))
				rect = text.get_rect()
				rx = x * TILE_SIZE[0]
				ry = y * TILE_SIZE[1]
				rect.center = (rx + TILE_SIZE[0]/2, ry + TILE_SIZE[1]/2)
				self.screen.blit(text, rect)

	def do_load(self):
		print 'Load'

	def do_save(self):
		print 'Save'

	def start_game(self, mapname):
		print "Loading game"
		print "Map: ", mapname
		print "Network game: ", self.network
		print "Hosting: ", self.network_host
		print "Selected IP: ", self.ip_input.value
		print "Selected Port: ", self.port_input.value

	def do_done(self):
		self.done = True

	def container_click(self, event, container):
		i = 0
		for b in container.children:
			for c in b.child_buttons:
				if c.visible:
					if c.contains(*event.pos):
						f = c.function[0]
						f(c.function[1])
						i = 1
						break
		if i == 0:
			for b in container.children:
				if b.parent_button.contains(*event.pos):
					b.parent_button.toggle()
					b.enable_buttons()
					break

	def click(self, event):
		for b in self.buttons:
			if b.contains(*event.pos):
				f = b.function[0]
				f(b.function[1])
				break

	def loop(self):
		area = None
		start = None
		tool = None

		self.done = False

		while not self.done:
			events = pygame.event.get()
			self.screen.fill(COLOR_BG)
			self.draw()
	
			if self.ip_input_enabled:
				self.ip_input.update(events)
			elif self.port_input_enabled:
				self.port_input.update(events)

			# blit txtbx on the sceen
			#if not self.network_host:
			self.ip_input.draw(self.screen)
			self.port_input.draw(self.screen)

			pygame.display.flip()

			for event in events:
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						self.click(event)
						self.container_click(event, self.sidebar_container)
				if event.type == pygame.QUIT:
					sys.exit()

			time.sleep(0.05)

if __name__ == "__main__":
	mapname = None
	if len(sys.argv) >= 2:
		mapname = sys.argv[1]

	screen = init_pygame()
	win = MapSelection(screen, "map_new.txt", True, True)
	win.loop()

