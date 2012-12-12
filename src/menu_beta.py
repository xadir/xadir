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
	def __init__(self, width=1200, height=720):
		pygame.init()
		self.width = width
		self.height = height
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.clock = pygame.time.Clock()
		self.fps = 30

		menu_size = (400, 400)
		self.menu = UIContainer(None, (20, 20), menu_size, self.screen, True)
		#self.menu = UIContainer(None, ((self.width - menu_size[0]) / 2, (self.height - menu_size[1]) / 2), menu_size, self.screen, True)
		new_game = Button(self.menu, self.screen, 0, 0, 400, 60, [["New Game", (4,4)]], None)
		self.menu.children.append(new_game)
		load_game = Button(self.menu, self.screen, 0, 80, 400, 60, [["Load Game", (4,4)]], None)
		self.menu.children.append(load_game)
		settings = Button(self.menu, self.screen, 0, 160, 400, 60, [["Settings", (4,4)]], None)
		self.menu.children.append(settings)
		quit = Button(self.menu, self.screen, 0, 240, 400, 60, [["Quit", (4,4)]], None)
		self.menu.children.append(quit)

	def loop(self):
		title_alpha = 0
		load_finished = False
		title_image = load_image("Xadir.png", None, 3)
		title_rect = title_image.get_rect()
		title_rect.centerx = self.width / 2
		title_rect.centery = self.height / 2
		title_image.set_alpha(title_alpha)
		while 1:
			events = pygame.event.get()
			self.screen.fill((0, 0, 0))
			if title_alpha < 255:			
				title_alpha += 1+ (title_alpha / 8)
				title_image.set_alpha(title_alpha)
			else:
				load_finished = True
			self.screen.blit(title_image, title_rect)
			if load_finished:
				self.menu.draw()
			pygame.display.flip()
			for event in events:
				if event.type == pygame.QUIT:
					sys.exit()

			self.clock.tick(self.fps)

if __name__ == "__main__":

	win = Menu()
	win.loop()

