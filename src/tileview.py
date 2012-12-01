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
			self.screen.fill((0, 0, 0))
			for y in range(tile_rows):
				for x in range(tile_cols):
					self.screen.fill((255, 0, 255), (x * framed_x, y * framed_y, size_x, size_y))
					self.screen.blit(tiles[y][x], (x * framed_x, y * framed_y))
			pygame.display.flip()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
			time.sleep(0.05)

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print 'syntax: %s FILE [SIZE_X [SIZE_Y]]' % (sys.argv[0], )
		sys.exit()

	# Size of individual tiles
	size_x = int(sys.argv[2]) if len(sys.argv) >= 3 else 16
	size_y = int(sys.argv[3]) if len(sys.argv) >= 4 else size_x

	# Size with borders
	framed_x = size_x + 1
	framed_y = size_y + 1

	# Window must be initialized before tiles can be loaded
	win = TileView()

	# Load tiles
	tiles = load_tiles(sys.argv[1], (size_x, size_y), (255, 0, 255))

	# Tile table size
	tile_cols = len(tiles[0])
	tile_rows = len(tiles)

	# Needed window size
	width = tile_cols * framed_x - 1
	height = tile_rows * framed_y - 1

	# Resize window to image size
	win.screen = pygame.display.set_mode((width, height))

	win.loop()

