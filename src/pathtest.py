import sys, time
import pygame
from grid import *
from algo import *

SIZE = 15
COUNT = 10

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

class PathTest:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((COUNT*(SIZE+1)-1, COUNT*(SIZE+1)-1))
		self.grid = Grid(COUNT, COUNT, default = 0)
		self.colors = {0: (255, 255, 255), 1: (0, 0, 0)}
		self.src = (0, 0)
		self.dst = (COUNT-1, COUNT-1)

	def loop(self):
		down = None
		moved = False

		while 1:
			self.screen.fill((127, 127, 127))
			for y in range(COUNT):
				for x in range(COUNT):
					self.screen.fill(self.colors[self.grid[x, y]], (x*(SIZE+1), y*(SIZE+1), SIZE, SIZE))

			path = shortest_path(self.grid, self.src, self.dst, lambda g, v: sorted([key for key, value in g.env_items(v) if not value], key = lambda u: (u[0]-v[0])**2+(u[1]-v[1])**2 ))
			for cur, nxt in zip(path[:-1], path[1:]):
				pygame.draw.aaline(self.screen, (0, 255, 0), (SIZE/2+cur[0]*(SIZE+1), SIZE/2+cur[1]*(SIZE+1)), (SIZE/2+nxt[0]*(SIZE+1), SIZE/2+nxt[1]*(SIZE+1)))

			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				elif event.type == pygame.MOUSEBUTTONDOWN:
					down = event.button
					moved = False
				elif event.type == pygame.MOUSEBUTTONUP:
					down = None
					if not moved:
						x, y = event.pos
						setattr(self, {1: 'src', 3: 'dst'}[event.button], (x/(SIZE+1), y/(SIZE+1)))
				elif event.type == pygame.MOUSEMOTION:
					moved = True
					if down is not None:
						x, y = event.pos
						self.grid[x/(SIZE+1), y/(SIZE+1)] = {3: 0, 1: 1}[down]

			time.sleep(0.05)

if __name__ == "__main__":
	win = PathTest()
	win.loop()

