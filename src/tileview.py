import os, sys, time
import pygame
from pygame.locals import *
from resources import *
from config import *

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

class TileView:
	"""Main class for init and creation of game."""

	def __init__(self, width=640, height=480):
		pygame.init()
		self.width = width
		self.height = height
		self.screen = pygame.display.set_mode((self.width, self.height))

	def loop(self):
		while 1:
			for y in range(len(tiles)):
				for x in range(len(tiles[y])):
					self.screen.blit(tiles[y][x], (x*(SIZE[0]+1), y*(SIZE[1]+1)))
			pygame.display.flip()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
			time.sleep(0.05)

# XXX: window size from image size
if __name__ == "__main__":
	if len(sys.argv) < 2:
		print 'syntax: %s FILE [SIZE_X [SIZE_Y]]' % (sys.argv[0], )
		sys.exit()

	size_x = int(sys.argv[2]) if len(sys.argv) >= 3 else 16
	size_y = int(sys.argv[3]) if len(sys.argv) >= 4 else size_x
	SIZE = (size_x, size_y)

	win = TileView()

	tiles = load_tiles(sys.argv[1], SIZE, (255, 0, 255))

	win.loop()

