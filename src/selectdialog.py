import os, sys, time
import pygame
from pygame.locals import *
from resources import *
from UI import *

from tiles import *

clamp_below = lambda v, maxv: min(v, maxv)
clamp_above = lambda v, minv: max(v, minv)
clamp = lambda v, minv, maxv: min(max(v, minv), maxv)
clamp_pos = lambda (x, y), (width, height): (clamp(x, 0, width - 1), clamp(y, 0, height - 1))
clamp_elem = lambda (x, y), (width, height), (area_width, area_height): clamp_pos((x, y), (area_width - width + 1, area_height - height + 1))

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

class FakeGrid:
	def __init__(self, size):
		self.cell_size = size

class Window:
	def __init__(self, screen):
		self.screen = screen

		self.background = pygame.Surface(self.screen.get_size())
		self.background.fill((0, 0, 0))

		self.fps = 30
		self.clock = pygame.time.Clock()

		self.res = Resources(None)

		self.elem = TextList([str(i) + s for i in range(10) for s in ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']], (100, 200))

		self.sprites = pygame.sprite.LayeredDirty(_time_threshold = 1000.0)
		self.sprites.set_clip()
		self.sprites.add(self.elem)

	def draw(self, frames = 1):
		for i in range(frames):
			self.clock.tick(self.fps)
			self.sprites.update()
			self.sprites.clear(self.screen, self.background)
			# Update layers
			self.sprites._spritelist.sort(key = lambda sprite: sprite._layer)
			self.sprites.draw(self.screen)
			pygame.display.flip()

	def loop(self):
		self.done = False
		while not self.done:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.done = True
				self.elem.event(event)

			self.draw()

class Button(UIObject):
	def __init__(self, parent, rel_pos, size):
		UIObject.__init__(self, parent, rel_pos, size)
		self.down = None

	def event(self, ev):
		if ev.type == pygame.MOUSEBUTTONDOWN:
			if self.contains(*ev.pos):
				self.down = self.translate(*ev.pos)
		if ev.type == pygame.MOUSEBUTTONUP:
			if self.contains(*ev.pos) and self.down:
				self.clicked(ev)
			self.down = None

	def clicked(self, ev):
		raise NotImplemented, 'This method must be implemented by base classes'

class Draggable(Button):
	def __init__(self, parent, rel_pos, size):
		Button.__init__(self, parent, rel_pos, size)
		assert parent.size[0] >= size[0] and parent.size[1] >= size[1]

	def event(self, ev):
		Button.event(self, ev)
		if ev.type == pygame.MOUSEMOTION:
			if self.down:
				x, y = self.parent.translate(*ev.pos)
				pos = x - self.down[0], y - self.down[1]
				self.rel_pos = clamp_elem(pos, self.size, self.parent.size)

	def clicked(self, ev):
		pass

class ScrollBar(UIObject):
	def __init__(self, parent, rel_pos, size, knob_size, final_size):
		UIObject.__init__(self, parent, rel_pos, size)
		self.knob = Draggable(self, (0, 0), knob_size)
		self.final_size = final_size

	def _get_knob_pos(self):
		leeway = tuple(self.size[i] - self.knob.size[i] for i in range(2))
		return tuple(self.knob.rel_pos[i] * self.final_size[i] / leeway[i] if leeway[i] else 0 for i in range(2))
	knob_pos = property(_get_knob_pos)

	def event(self, ev):
		self.knob.event(ev)

class TextList(StateTrackingSprite):
	def __init__(self, items, size, tickless = True):
		StateTrackingSprite.__init__(self)

		self.image = pygame.Surface(size)
		self.rect = pygame.Rect((0, 0), size)

		self.font = pygame.font.Font(FONT, int(16*FONTSCALE))
		self.linecount = (size[1] - 1) / self.font.get_linesize() + 1

		self.tickless = tickless

		if self.tickless:
			target_size = len(items) * self.font.get_linesize() - size[1]
		else:
			target_size = len(items) - size[1] / self.font.get_linesize()

		self.scroll = ScrollBar(UIRoot(), (size[0]-10, 0), (10, size[1]), (10, 20), (0, clamp_above(target_size, 0)))

		self.items = items
		self.size = size
		self.pos = 0

	def event(self, ev):
		self.scroll.event(ev)

	def get_state(self):
		divisor = self.font.get_linesize() if self.tickless else 1
		index, offset = divmod(self.scroll.knob_pos[1], divisor)
		return self.scroll.knob.rel_pos[1], self.items[index:index+self.linecount], offset

	def redraw(self):
		self.image.fill((255, 255, 255))
		y = -self.state[2]
		for item in self.state[1]:
			text = self.font.render(item, True, (0, 0, 0))
			self.image.blit(text, (0, y))
			y += self.font.get_linesize()
		self.image.fill((127, 127, 127), (self.size[0]-10, 0, 10, self.size[1]))
		self.image.fill((63, 63, 63), (self.size[0]-10, self.state[0], 10, 20))

if __name__ == "__main__":
	screen = init_pygame()

	win = Window(screen)
	win.loop()

