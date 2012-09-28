import os, sys, time
import pygame
from pygame.locals import *
from resources import *
from config import *

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
		"""
		map_UIComponent = UIComponent(x, y, w, h)
		mapfont = pygame.font.Font(None, 30)
		maptext = mapfont.render(mapname, True, (255,255, 255), (159, 182, 205))
		maprect = maptext.get_rect()
		maprect.left = (x + 5)
		maprect.centery = (y + (h/2))
		"""
		self.maplinks.append(Button(x, y, w, h, mapname, self.screen, self.select_map))

	def update_maplist(self):
		maps = self.list_maps()
		print "from update_maplist"
		print maps
		print
		x = 0
		y = 0
		w = 300
		h = 40
		margin = 2
		self.maplist = []
		for m in maps:
			self.maplist.append(self.add_map(m, x, y, h, w))
			y = (y + h) + margin

	def write_button(self, surface, text, x, y):
		buttontext = self.buttonfont.render(text, True, (255,255, 255), (159, 182, 205))
		buttonrect = buttontext.get_rect()
		buttonrect.centerx = x
		buttonrect.centery = y
		surface.blit(buttontext, buttonrect)

	def load_map(self, mapname):
		print "loading map: " + mapname

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

		self.buttons.append(Button(20, 300, 80, 40, "Load", self.screen, self.load_map))
		self.buttons.append(Button(120, 300, 80, 40, "Edit", self.screen, self.edit_map))
		self.buttons.append(Button(70, 350, 160, 40, "Quit", self.screen, self.quit))
		"""
		load = UIComponent(20, 300, 80, 40)
		edit = UIComponent(120, 300, 80, 40)
		quit = UIComponent(0, 350, 160, 40)
		"""

		area = None
		while 1:
			self.screen.fill((255, 255, 255))
			"""
			self.write_button(self.screen, "load", 50, 300)
			self.write_button(self.screen, "edit", 170, 300)
			self.write_button(self.screen, "quit", 80, 350)
			"""
			for b in self.buttons:
				b.draw()
			pygame.display.flip()
			#for m in maplist:
			#	print m[0]
			#	self.screen.blit(m[2], m[3])
			for event in pygame.event.get():
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						#for m in maplist:
						#	if m[1].contains(*event.pos):
						#		print "selected: " + m[0]
						#		self.mapname = m[0]
						#		area = 'maplist'
						for b in self.buttons:
							if b.get_UI().contains(*event.pos):
								area = b.get_name()
						"""
						if load.contains(*event.pos):
							area = 'load'
						elif edit.contains(*event.pos):
							area = 'edit'
						elif quit.contains(*event.pos):
							area = 'quit'
						"""
				elif event.type == pygame.MOUSEBUTTONUP:
					if event.button == 1:
						#if area == 'maplist' and maplist.contains(*event.pos):
						#	print "selected map %d" % (mapname)
						for b in self.buttons:
							if area == b.get_name() and b.get_UI().contains(*event.pos):
								f = b.get_function()
								if b.get_name() == "Quit":
									f()
								else:
									f(self.mapname)
						"""
						if area == 'load' and load.contains(*event.pos):
							print "loading map %d for game" % (mapname)
						if area == 'edit' and edit.contains(*event.pos):
							print "loading map %d for mapeditor" % (mapname)
						if area == 'quit' and quit.contains(*event.pos):
							sys.exit()
						"""
						area = None
				elif event.type == pygame.QUIT:
					sys.exit()

			time.sleep(0.05)

class Button:
	def __init__(self, x, y, width, height, name, surface, function):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.name = name
		self.function = function
		self.buttonUI = UIComponent(x, y, width, height)
		self.surface = surface
		self.create_text(self.name)

	def create_text(self, text):
		self.buttonfont = pygame.font.Font(None, 40)
		self.buttontext = self.buttonfont.render(text, True, (255,255, 255), (159, 182, 205))
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

	def get_UI(self):
		return self.buttonUI

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

	win = Menu()
	win.loop()

