"""""""""""""""""""""""""""""""""
@name: UI-Class
@author: Heikki Juva

@description:
Contains all the UI-components
used in Xadir.
"""""""""""""""""""""""""""""""""

import sys, time
import pygame
from resources import *

class UIRoot:
	def __init__(self):
		self.x = self.y = 0

class UIObject(object):
	"""Base class of everything with coordinates.

	Instances have the following attributes:
	- pos     = x, y          = position on screen
	- rel_pos = rel_x, rel_y  = position relative to parent
	- size    = width, height = size
	"""
	def __init__(self, parent, rel_pos, size = None):
		if not parent:
			parent = UIRoot()
		self.parent = parent
		self.rel_pos = rel_pos
		if size:
			self.size = size

	def _get_pos(self): return (self.x, self.y)
	def _set_pos(self, pos): (self.x, self.y) = pos
	pos = property(_get_pos, _set_pos)

	def _get_rel_x(self): return self.x - self.parent.x
	def _set_rel_x(self, x): self.x = self.parent.x + x
	rel_x = property(_get_rel_x, _set_rel_x)

	def _get_rel_y(self): return self.y - self.parent.y
	def _set_rel_y(self, y): self.y = self.parent.y + y
	rel_y = property(_get_rel_y, _set_rel_y)

	def _get_rel_pos(self): return (self.rel_x, self.rel_y)
	def _set_rel_pos(self, pos): (self.rel_x, self.rel_y) = pos
	rel_pos = property(_get_rel_pos, _set_rel_pos)

	def _get_size(self): return (self.width, self.height)
	def _set_size(self, size): (self.width, self.height) = size
	size = property(_get_size, _set_size)

	def _get_rect(self): return pygame.Rect(self.x, self.y, self.width, self.height)
	rect = property(_get_rect)

	def contains(self, x, y):
		return x >= self.x and y >= self.y and x < self.x + self.width and y < self.y + self.height

	def translate(self, x, y):
		return x - self.x, y - self.y

class UIGridObject(UIObject):
	"""Base class of everything that's on a grid.

	Instances have the following attributes:
	- pos      = x, y           = position on screen
	- rel_pos  = rel_x, rel_y   = position relative to parent
	- grid_pos = grid_x, grid_y = position on grid
	- size     = width, height  = size
	"""
	def __init__(self, grid, grid_pos):
		UIObject.__init__(self, grid, (0, 0), grid.cell_size)
		self.grid = grid
		self.grid_pos = grid_pos

	def _get_grid_x(self): return self.rel_x / self.width
	def _set_grid_x(self, x): self.rel_x = x * self.width
	grid_x = property(_get_grid_x, _set_grid_x)

	def _get_grid_y(self): return self.rel_y / self.height
	def _set_grid_y(self, y): self.rel_y = y * self.height
	grid_y = property(_get_grid_y, _set_grid_y)

	def _get_grid_pos(self): return (self.grid_x, self.grid_y)
	def _set_grid_pos(self, pos): (self.grid_x, self.grid_y) = pos
	grid_pos = property(_get_grid_pos, _set_grid_pos)

class UIContainer(UIObject):
	def __init__(self, parent, rel_pos, size, children):
		UIObject.__init__(self, parent, rel_pos, size)
		self.children = children

	def click(self, x, y):
		for child in self.children:
			propagate = child.click(x, y)
			if not propagate:
				return True

	def update(self):
		for child in self.children:
			child.update()

	def draw(self):
		for child in self.children:
			child.draw()

# XXX: Deprecated
class UIComponent(UIObject):
	def __init__(self, x, y, width, height):
		UIObject.__init__(self, None, (x, y), (width, height))

class Tile(pygame.sprite.Sprite):
	def __init__(self, image, rect=None, layer=0):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = image.get_rect()
		self._layer = layer
		if rect is not None:
			self.rect = rect

class Func_Button(UIObject):
	def __init__(self, parent, x, y, width, height, border, bg_color, border_color, selected_color, text, image, fontsize, surface, function, visible, selected, hideable):
		UIObject.__init__(self, parent, (x, y), (width, height))
		self.radius = 9
		self.border_width = border
		self.visible = visible
		self.function = function
		self.surface = surface
		self.fontsize = fontsize
		self.bg_color = bg_color
		self.border_color = border_color
		self.selected_color = selected_color
		self.images = image
		self.selected = selected
		self.hideable = hideable
		
		self.border = self.add_round_rect(pygame.Rect(self.x, self.y, self.width + (self.border_width * 2), self.height + (self.border_width * 2)), border_color, self.radius)
		self.background = self.add_round_rect(pygame.Rect(self.x + self.border_width, self.y + self.border_width, self.width, self.height), bg_color, self.radius)
		
		self.texts = []
		if text != None:
			for t in text:
				self.add_text(t[0], t[1], self.fontsize)

	def add_text(self, string, coords, fontsize):
		font = pygame.font.Font(FONT, int(fontsize*FONTSCALE))
		text = font.render(string, True, (0, 0, 0), self.bg_color)
		rect = text.get_rect()
		if coords != None:
			rect.x = self.x + coords[0]
			rect.y = self.y + coords[1]
		else:
			rect.centerx = self.x + (self.width/2)
			rect.centery = self.y + (self.height/2)
		self.texts.append([text, rect])

	def get_function(self):
		return self.function
		
	def show(self):
		self.visible = True
	
	def hide(self):
		self.visible = False
		
	def select(self):
		self.selected = True
		self.border = self.add_round_rect(pygame.Rect(self.x, self.y, self.width + (self.border_width * 2), self.height + (self.border_width * 2)), self.selected_color, self.radius)
		
	def unselect(self):
		self.selected = False
		self.border = self.add_round_rect(pygame.Rect(self.x, self.y, self.width + (self.border_width * 2), self.height + (self.border_width * 2)), self.border_color, self.radius)
		
	def toggle(self):
		if self.selected:
			self.select()
		else:
			self.unselect()
		
	def add_round_rect(self, rect, color, radius=10):

		"""
		AAfilledRoundedRect(surface,rect,color,radius=0.4)

		surface : destination
		rect    : rectangle
		color   : rgb or rgba
		radius  : 0 <= radius <= 1
		"""

		rect         = Rect(rect)
		color        = Color(*color)
		alpha        = color.a
		color.a      = 0
		pos          = rect.topleft
		rect.topleft = 0,0
		rectangle    = pygame.Surface(rect.size,SRCALPHA)

		circle       = pygame.Surface([min(rect.size)*3]*2,SRCALPHA)
		pygame.draw.ellipse(circle,(0,0,0),circle.get_rect(),0)
		circle       = pygame.transform.smoothscale(circle,[int(radius)]*2)

		radius              = rectangle.blit(circle,(0,0))
		radius.bottomright  = rect.bottomright
		rectangle.blit(circle,radius)
		radius.topright     = rect.topright
		rectangle.blit(circle,radius)
		radius.bottomleft   = rect.bottomleft
		rectangle.blit(circle,radius)

		rectangle.fill((0,0,0),rect.inflate(-radius.w,0))
		rectangle.fill((0,0,0),rect.inflate(0,-radius.h))

		rectangle.fill(color,special_flags=BLEND_RGBA_MAX)
		rectangle.fill((255,255,255,alpha),special_flags=BLEND_RGBA_MIN)

		return [rectangle, pos]
	
	def toggle_visibility(self):
		if self.hideable:
			if self.visible: self.visible = False
			else: self.visible = True

	def draw(self):
		self.surface.blit(self.border[0], self.border[1])
		self.surface.blit(self.background[0], self.background[1])
		if self.images != None:
			for i in self.images:
				try:
					rect = i[0].get_rect()
					rect.x = self.x + i[1][0]
					rect.y = self.y + i[1][1]
					self.surface.blit(i[0], rect)
				except AttributeError:
					rect = i[0].rect
					rect.x = self.x + i[1][0]
					rect.y = self.y + i[1][1]
					self.surface.blit(i[0].image, rect)
		for t in self.texts:
			self.surface.blit(t[0], t[1])
			
class CascadeButton(UIComponent):
	def __init__(self, parent, x=0, y=0):
		#icon = pygame.image.load(os.path.join(GFXDIR, "test_icon.png"))
		UIComponent.__init__(self, x, y, width, height)
		self.race_name = race_name
		self.sprite_file = sprite_file
		self.stat_file = stat_file
		self.surface = surface
		self.x = x
		self.y = y
		self.load_tile()
		self.child_buttons = []
		self.parent_button = FuncButton(x, y, self.race_tile.rect.width + 10, self.race_tile.rect.height + 20, 2, (200, 200, 200), (50, 50, 50), (150, 150, 150), None, [[self.race_tile, (7, 0)]], 20, self.surface, self.enable_buttons, True)
		self.child_buttons.append(FuncButton(x, y-25, self.race_tile.rect.width + 10, 20, 2, (200, 200, 200), (50, 50, 50), (150, 150, 150), [["Equip", None]], None, 20, self.surface, self.button_click, False))
		self.child_buttons.append(FuncButton(x, y+self.race_tile.rect.height+25, self.race_tile.rect.width + 10, 20, 2, (200, 200, 200), (50, 50, 50), (150, 150, 150), [["Sell", None]], None, 20, self.surface, self.button_click, False))

	def load_tile(self):
		self.race_tile = race_tile(self.race_name).get_tile(self.x, self.y, '270')
	
	def load_text(self):
		print GFXDIR
		print self.stat_file
		path = os.path.join(GFXDIR, self.stat_file)
		f = open(path, 'r')
		
		self.race_stats = {}
		# iterate over the lines in the file
		for line in f:
			# split the line into a list of column values
			columns = line.split(',')
			# clean any whitespace off the items
			columns = [col.strip() for col in columns]
			stats = []
			for i in range(1,len(columns)):
				temp = columns[i].split('=')
				temp = [col.strip() for col in temp]
				stats.append(temp)
			self.race_stats[columns[0]] = stats
			
		f.close()
		
	def button_click(self):
		print "Clicked button"
		
	def enable_buttons(self):
		for b in self.child_buttons:
			b.toggle_visibility()
