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

class MapEditor:
	def __init__(self, width=640, height=480):
		pygame.init()
		self.width = width
		self.height = height
		self.screen = pygame.display.set_mode((self.width, self.height))

		self.tiles = load_named_tiles('placeholder_tilemap', ORIG_TILE_SIZE, (255, 0, 255))
		tools, size, _ = load_map('tools.txt')

		self.grid = Grid(29, 29)
		self.tools = Grid(9, 29)

		for y, row in enumerate(tools):
			for x, tile_name in enumerate(row):
				self.tools[x, y] = tile_name

		# XXX: add tools that arent specified in toolfile

	def draw(self):
		for (x, y), tile in self.tools.items():
			if tile:
				self.screen.blit(self.tiles[tile], (x * 17, y * 17))

		self.screen.fill((63, 63, 63), pygame.Rect(154, 0, 4, 480))

		for (x, y), tile in self.grid.items():
			if tile:
				self.screen.blit(self.tiles[tile], (160 + x * 17, y * 17))

	def loop(self):
		left = UIComponent(0, 0, 160, 480)
		right = UIComponent(160, 0, 480, 480)

		area = None
		start = None
		tool = None
		while 1:
			self.screen.fill((0, 0, 0))
			self.draw()
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.MOUSEBUTTONDOWN:
					if left.contains(*event.pos):
						area = 'left'
					elif right.contains(*event.pos):
						area = 'right'
					start = event.pos
				elif event.type == pygame.MOUSEBUTTONUP:
					if area == 'left' and left.contains(*event.pos):
						x, y = left.translate(*event.pos)
						x, y = x/17, y/17
						tool = self.tools[x, y]
					if area == 'right' and right.contains(*event.pos):
						x, y = right.translate(*event.pos)
						x, y = x/17, y/17
						self.grid[x, y] = tool
					area = None
					start = None
				elif event.type == pygame.MOUSEMOTION:
					if area == 'right' and right.contains(*event.pos):
						x, y = right.translate(*event.pos)
						x, y = x/17, y/17
						self.grid[x, y] = tool
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

if __name__ == "__main__":
	#if len(sys.argv) < 2:
	#	print 'syntax: %s FILE' % (sys.argv[0], )
	#	sys.exit()

	win = MapEditor()
	win.loop()

