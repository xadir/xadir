import os, sys, time
import pygame
try:
	import pygame._view # Because py2exe, that's why (should really probably do this in setup.py...)
except ImportError:
	pass
from pygame.locals import *
from resources import *
from config import *
from chartest import *
from UI import *
import game
import eztext

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

class Menu:
	def __init__(self, screen):
		self.screen = screen
		self.width, self.height = self.screen.get_size()
		self.titlefield = pygame.Surface((1200, 350))
		self.titlefield_rect = pygame.Rect(0, 0, 1200, 350)
		self.titlefield.fill((50, 50, 50))
		self.sidebar = pygame.Surface((200, 360))
		self.sidebar_rect = pygame.Rect(0, 350, 200, 360)
		self.sidebar.fill((159, 182, 205))
		self.mapfield = pygame.Surface((480, 360))
		self.mapfield_rect = pygame.Rect(202, 350, 480, 360)
		self.mapfield.fill((100, 100, 100))
		self.playerfield = pygame.Surface((514, 360))
		self.playerfield_rect = pygame.Rect(684, 350, 514, 360)
		self.playerfield.fill((150, 150, 150))
		self.buttonfont = pygame.font.Font(FONT, int(40*FONTSCALE))
		self.mapname = "nomap"
		self.tiletypes = load_named_tiles('placeholder_tilemap24', ORIG_TILE_SIZE, (255, 0, 255), 1)
		
		self.txtbx = eztext.Input(x=690, y=360, maxlength=45, color=(0,0,0), prompt='Team name: ')

		self.buttons = []
		self.maplist = []
		self.maplinks = []
		self.race_buttons = []

	def list_maps(self):
		maps = os.listdir(MAPDIR)
		return maps

	def add_map(self, mapname, x, y, w, h):
		self.maplinks.append(Button(x, y, w, h, mapname, 20, self.screen, self.select_map))

	def update_maplist(self):
		maps = self.list_maps()
		i = 0
		while i < len(maps):
			if maps[i] == "tools.txt":
				maps.pop(i)
				i = i - 1
			else:
				try:
					map, mapsize, spawns = load_map(maps[i])
					if mapsize != (20,15):
						maps.pop(i)
						i = i - 1
				except:
					maps.pop(i)
					i = i - 1
			i = i + 1
		x = 10
		y = 360
		w = 300
		h = 20
		margin = 2
		self.maplist = []
		for m in maps:
			self.maplist.append(self.add_map(m, x, y, h, w))
			self.add_map(m, x, y, w, h)		
			y = (y + h) + margin

	def write_button(self, surface, text, x, y):
		buttontext = self.buttonfont.render(text, True, (255,255, 255), (159, 182, 205))
		buttonrect = buttontext.get_rect()
		buttonrect.centerx = x
		buttonrect.centery = y
		surface.blit(buttontext, buttonrect)

	def load_map(self, mapname):
		if self.mapname == 'nomap': print "No map selected"
		else:
			print "starting game"
			game.start_game(self.mapname)

	def edit_map(self, mapname):
		print "loading map: " + mapname

	def select_map(self, mapname):
		self.mapname = mapname
		print "selected map: " + mapname
		map, mapsize, spawns = load_map(self.mapname)
		self.map = preview_map(map, *mapsize, tiletypes = self.tiletypes)
		self.map_sprites = self.map.get_sprites()
		self.mapfield.fill((100, 100, 100))
		self.screen.blit(self.mapfield, self.mapfield_rect)
		self.map_sprites.draw(self.screen)

	def get_sprites(self):
		return self.sprites

	def get_map(self):
		return self.map
		
	def add_char_button(self, race_name, x, y):
		self.race_buttons.append(race_preview(race_name=race_name, x=x, y=y))

	def quit(self):
		sys.exit()

	def loop(self):
		self.update_maplist()
		#mapimage = UIComponent(300, 0, 480, 340)

		self.buttons.append(Button(20, 600, 80, 40, "Load", 40, self.screen, self.load_map))
		self.buttons.append(Button(120, 600, 80, 40, "Edit", 40, self.screen, self.edit_map))
		self.buttons.append(Button(57, 650, 160, 60, "Quit", 60, self.screen, self.quit))
		
		"""
		self.add_char_button('Human', 690, 390)
		self.add_char_button('Human2', 790, 390)
		self.add_char_button('Human3', 890, 390)
		self.add_char_button('Devil', 990, 390)
		self.add_char_button('Elf', 1090, 390)
		self.add_char_button('Alien', 690, 530)
		self.add_char_button('WhiteGuy', 790, 530)
		self.add_char_button('Medusa', 890, 530)
		self.add_char_button('Dragon', 990, 530)
		self.add_char_button('Taurus', 1090, 530)
		"""
		"""
		self.add_char_button('Squid', 690, 600)
		self.add_char_button('GreyGuy', 790, 600)
		self.add_char_button('Imhotep', 890, 700)
		self.add_char_button('Wolf', 990, 700)
		"""
		title_image = load_image("title.png", -1)
		self.titlefield.blit(title_image, title_image.get_rect())

		area = None
		self.screen.fill((40, 40, 40))
		self.screen.blit(self.titlefield, self.titlefield_rect)
		self.screen.blit(self.sidebar, self.sidebar_rect)
		self.screen.blit(self.mapfield, self.mapfield_rect)
		self.screen.blit(self.playerfield, self.playerfield_rect)
		
		self.select_map(self.maplinks[0].get_name())
		
		while 1:
			events = pygame.event.get()
			self.playerfield.fill((150, 150, 150))
			self.screen.blit(self.playerfield, self.playerfield_rect)
			# update txtbx
			self.txtbx.update(events)
			# blit txtbx on the sceen
			self.txtbx.draw(self.screen)
			for r in self.race_buttons:
				r.draw(self.screen)
			for b in self.buttons:
				b.draw()
			for m in self.maplinks:
				m.draw()
			pygame.display.flip()
			for event in events:
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						for m in self.maplinks:
							if m.contains(*event.pos):
								area = 'maplist'
						for b in self.buttons:
							if b.contains(*event.pos):
								area = b.get_name()
						for p in self.race_buttons:
							if p.contains(*event.pos):
								p.toggle()
				elif event.type == pygame.MOUSEBUTTONUP:
					if event.button == 1:
						for m in self.maplinks:
							if area == 'maplist' and m.contains(*event.pos):
								f = m.get_function()
								f(m.get_name())
						for b in self.buttons:
							if area == b.get_name() and b.contains(*event.pos):
								f = b.get_function()
								if b.get_name() == "Quit":
									f()
								else:
									f(self.mapname)
						area = None
				elif event.type == pygame.QUIT:
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

class Button(UIComponent):
	def __init__(self, x, y, width, height, name, fontsize, surface, function):
		UIComponent.__init__(self, x, y, width, height)
		self.name = name
		self.function = function
		self.surface = surface
		self.fontsize = fontsize
		self.create_text(self.name, self.fontsize)

	def create_text(self, text, fontsize):
		self.buttonfont = pygame.font.Font(FONT, int(fontsize*FONTSCALE))
		self.buttontext = self.buttonfont.render(text, True, (0, 0, 0), (159, 182, 205))
		self.buttonrect = self.buttontext.get_rect()
		self.buttonrect.left = self.x
		self.buttonrect.top = self.y
		self.buttonrect.width = self.width
		self.buttonrect.height = self.height

	def get_function(self):
		return self.function

	def get_text(self):
		return self.buttontext

	def get_rect(self):
		return self.buttonrect

	def get_name(self):
		return self.name

	def draw(self):
		self.surface.blit(self.buttontext, self.buttonrect)

class preview_map:
	"""Map class to create the background layer, holds any static and dynamical elements in the field."""
	def __init__(self, map, width, height, tiletypes):
		self.width = width
		self.height = height
		self.map = map
		self.sprites = pygame.sprite.LayeredUpdates()
		for y in range(self.height):
			for x in range(self.width):
				tiletype = self.map[y][x]
				tile = tiletypes[tiletype]
				#print x, y
				self.sprites.add(Tile(tile, pygame.Rect(202+x*ORIG_TILE_SIZE[0], 350+y*ORIG_TILE_SIZE[1], *ORIG_TILE_SIZE), layer = y))
	def get_sprites(self):
		return self.sprites

	def get_map(self):
		return self.map

class Tile(pygame.sprite.Sprite):
	def __init__(self, image, rect=None, layer=0):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = image.get_rect()
		self._layer = layer
		if rect is not None:
			self.rect = rect

if __name__ == "__main__":
	screen = init_pygame()
	win = Menu(screen)
	win.loop()

