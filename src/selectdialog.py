import os, sys, time
import pygame
from pygame.locals import *
from helpers import *
from resources import *
from UI import *

from tiles import *

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

class FakeGrid:
	def __init__(self, size):
		self.cell_size = size

root = UIRoot()

class Window:
	def __init__(self, screen):
		self.screen = screen

		self.background = pygame.Surface(self.screen.get_size())
		self.background.fill((0, 0, 0))

		self.fps = 30
		self.clock = pygame.time.Clock()

		self.res = Resources(None)

		tinylist = ['qwertyuiop', 'asdfghjkl', 'zxcvbnm']
		biglist = [str(i) + s for i in range(10) for s in tinylist]
		self.elems = [
			TextList(root, (10, 10), (100, 200), biglist),
			TextList(root, (120, 60), (100, 100), biglist),
			TextList(root, (230, 10), (100, 200), tinylist),
			TextList(root, (10, 220), (100, 200), biglist, tickless = False),
			TextList(root, (120, 270), (100, 100), biglist, tickless = False),
			TextList(root, (230, 220), (100, 200), tinylist, tickless = False),
		]

		self.sprites = pygame.sprite.LayeredDirty(_time_threshold = 1000.0)
		self.sprites.set_clip()
		self.sprites.add(self.elems)

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
				for elem in self.elems:
					elem.event(event)

			self.draw()

class Button(UIObject):
	def __init__(self, parent, rel_pos, size, clicked = None):
		UIObject.__init__(self, parent, rel_pos, size)
		self.down = None
		self._clicked = clicked

	def event(self, ev):
		if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
			if self.contains(*ev.pos):
				self.down = self.translate(*ev.pos)
		if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
			if self.contains(*ev.pos) and self.down:
				self.clicked(ev)
			self.down = None

	def clicked(self, ev):
		if self._clicked:
			self._clicked(self, ev)

class Draggable(Button):
	def __init__(self, parent, rel_pos, size, clicked = None, moved = None):
		Button.__init__(self, parent, rel_pos, size, clicked)
		assert parent.size[0] >= size[0] and parent.size[1] >= size[1]
		self._moved = moved

	def event(self, ev):
		Button.event(self, ev)
		if ev.type == pygame.MOUSEMOTION:
			if self.down:
				x, y = self.parent.translate(*ev.pos)
				pos = x - self.down[0], y - self.down[1]
				self.rel_pos = clamp_elem(pos, self.size, self.parent.size)
				self.moved(ev)

	def moved(self, ev):
		if self._moved:
			self._moved(self, ev)

class ScrollBar(UIObject):
	def __init__(self, parent, rel_pos, size, knob_size, final_size):
		UIObject.__init__(self, parent, rel_pos, size)
		self.knob = Draggable(self, (0, 0), knob_size)
		self.leeway = tuple(self.size[i] - self.knob.size[i] for i in range(2))
		self.range = final_size
		self._value = (0, 0)

	def _set_value(self, value):
		value = clamp_pos(value, self.range)
		self._value = value
		self.knob.rel_pos = scale_pos(value, self.range, self.leeway)

	def _get_value(self):
		# Return self._value if it still matches the position of the knob, otherwise recalculate it
		value = scale_pos(self._value, self.range, self.leeway)
		if value != self.knob.rel_pos:
			self._value = scale_pos(self.knob.rel_pos, self.leeway, self.range)
		return self._value

	value = property(_get_value, _set_value)

	def event(self, ev):
		self.knob.event(ev)

class TextList(StateTrackingSprite, UIObject):
	def __init__(self, parent, rel_pos, size, items, tickless = True, selected = None, format_item = None):
		StateTrackingSprite.__init__(self)
		UIObject.__init__(self, parent, rel_pos, size)

		self.image = pygame.Surface(size)

		self.font = pygame.font.Font(FONT, int(16*FONTSCALE))
		self.linesize = self.font.get_linesize()
		self.linecount = div_ceil(self.height, self.linesize)

		self.tickless = tickless
		self.ratios = [1, self.linesize]

		if self.tickless:
			self.ratios.reverse()

		target_size = len(items) * self.ratios[0] - self.height / self.ratios[1]

		bar_width, bar_height = 10, 20
		self.scroll = ScrollBar(self, (self.width - bar_width, 0), (bar_width, self.height), (bar_width, bar_height), (0, clamp_above(target_size, 0)))

		self.items = items
		self.sel = None

		self._selected = selected
		if format_item:
			self.format_item = format_item

	def event(self, ev):
		self.scroll.event(ev)
		value = self.scroll.value
		if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
			if self.contains(*ev.pos) and not self.scroll.contains(*ev.pos):
				pos = self.scroll.value[1] * self.ratios[1] + self.translate(*ev.pos)[1]
				index, offset = divmod(pos, self.linesize)
				self.sel = index if index != self.sel else None
				self.selected(ev)
		if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 4:
			if self.contains(*ev.pos):
				self.scroll.value = (value[0], value[1] - self.ratios[0])
		if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 5:
			if self.contains(*ev.pos):
				self.scroll.value = (value[0], value[1] + self.ratios[0])

	def get_state(self):
		index, offset = divmod(self.scroll.value[1], self.ratios[0])
		return len(self.items), self.items[index:index+self.linecount], self.scroll.knob.rel_y, index, offset, self.sel

	def redraw(self):
		self.scroll.range = (0, clamp_above(len(self.items) * self.ratios[0] - self.height / self.ratios[1], 0))
		total, items, knob_y, base, offset, sel = self.state
		self.image.fill((255, 255, 255))
		y = -offset
		for i, item in enumerate(items):
			if base + i == sel:
				self.image.fill((191, 191, 191), (0, max(y, 0), self.width, self.linesize + min(y, 0)))
			text = self.font.render(self.format_item(item), True, (0, 0, 0))
			self.image.blit(text, (0, y))
			y += self.linesize
		self.image.fill((127, 127, 127), (self.width - self.scroll.width, 0, self.scroll.width, self.height))
		self.image.fill((63, 63, 63), (self.width - self.scroll.width, knob_y, self.scroll.width, self.scroll.knob.height))

	def format_item(self, item):
		return item

	def selected(self, ev):
		if self._selected:
			self._selected(self, ev)

if __name__ == "__main__":
	screen = init_pygame()

	win = Window(screen)
	win.loop()

