import os, sys, time
import pygame
from pygame.locals import *
from resources import *
from config import *
import game

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

class Menu:
	def __init__(self, width=640, height=480):
		pygame.init()
		self.width = width
		self.height = height
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.sidebar = pygame.Surface((200, 480))
		self.sidebar_rect = pygame.Rect(0, 0, 200, 480)
		self.sidebar.fill((159, 182, 205))
		self.buttonfont = pygame.font.Font(None, 40)
		self.mapname = "nomap"

		self.buttons = []
		self.maplist = []
		self.maplinks = []

	def list_maps(self):
		maps = os.listdir(MAPDIR)
		print "from list_maps"
		print maps
		print
		return maps

	def add_map(self, mapname, x, y, w, h):
		self.maplinks.append(Button(x, y, w, h, mapname, 20, self.screen, self.select_map))

	def update_maplist(self):
		maps = self.list_maps()
		print "from update_maplist"
		print maps
		print
		x = 10
		y = 10
		w = 300
		h = 20
		margin = 2
		self.maplist = []
		for m in maps:
			self.maplist.append(self.add_map(m, x, y, h, w))
			self.add_map(m, x, y, w, h)
			print self.maplinks			
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

	def quit(self):
		sys.exit()

	def loop(self):
		self.update_maplist()
		#mapimage = UIComponent(300, 0, 480, 340)

		self.buttons.append(Button(20, 350, 80, 40, "Load", 40, self.screen, self.load_map))
		self.buttons.append(Button(120, 350, 80, 40, "Edit", 40, self.screen, self.edit_map))
		self.buttons.append(Button(57, 400, 160, 60, "Quit", 60, self.screen, self.quit))

		area = None
		self.screen.fill((0, 0, 0))
		self.screen.blit(self.sidebar, self.sidebar_rect)
		while 1:			
			for b in self.buttons:
				b.draw()
			for m in self.maplinks:
				m.draw()
			pygame.display.flip()
			for event in pygame.event.get():
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						for m in self.maplinks:
							if m.contains(*event.pos):
								area = 'maplist'						
						for b in self.buttons:
							if b.contains(*event.pos):
								area = b.get_name()
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
		self.buttonfont = pygame.font.Font(None, fontsize)
		self.buttontext = self.buttonfont.render(text, True, (255,255, 255), (105, 105, 105))
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

if __name__ == "__main__":

	win = Menu()
	win.loop()

