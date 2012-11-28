import sys, time
import pygame
from resources import *
from grid import *
from algo import *
from UI import *

SIZE = 15
COUNT = 10

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

class CharTest:

	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((600, 600))

		self.charfield = pygame.Surface((600, 600))
		self.charfield_rect = pygame.Rect(0, 0, 600, 600)
		self.charfield.fill((150,150,150))
		
		self.preview = []
		#self.preview.append(race_preview(race_name = 'Longear', x = 0, y = 0))
		#self.preview.append(race_preview(race_name = 'Longear', x = 100, y = 0))
		#self.preview.append(race_preview(race_name = 'Croco', x = 100, y = 0))
		self.preview.append(race_preview(race_name = 'Human', hair_name = 'd', x = 200, y = 0))
		#self.preview.append(race_preview(race_name = 'Dragon', x = 300, y = 0))
		#self.preview.append(race_preview(race_name = 'Croco', x = 100, y = 0))
		#self.preview.append(race_preview(race_name = 'Human', x = 200, y = 0))
		#self.preview.append(race_preview(race_name = 'Dragon', x = 300, y = 0))

		self.parent_buttons = []
		char1 = better_race_preview(race_name = 'Dragon', x = 300, y = 100, surface=self.screen)
		self.parent_buttons.append(char1)

	def loop(self):
		while 1:
			self.screen.fill((127, 127, 127))
			
			for i in range(len(self.preview)):
				self.preview[i].draw(self.screen)
			
			for p in self.parent_buttons:
				p.update_tiles()
				p.parent_button.draw()
				for c in p.child_buttons:
					if c.visible: c.draw()
			pygame.display.flip()

			"""
			for event in pygame.event.get():
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						for p in self.preview:
							if p.contains(*event.pos):
								p.toggle()
			"""
			for event in pygame.event.get():
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						for p in self.parent_buttons:
							for c in p.child_buttons:
								if c.visible:
									if c.contains(*event.pos):
										c.select()
										if c.hideable:
											p.toggle_visibility_buttons()
										c.unselect()
										f = c.get_function()
										f()
										break
							else:
								if p.parent_button.contains(*event.pos):
									p.parent_button.toggle()
									p.toggle_visibility_buttons()
							print
				elif event.type == pygame.QUIT:
					sys.exit()

			time.sleep(0.05)
			
class better_race_preview:
	def __init__(self, race_name, surface, sprite_file='race_sprites.txt', stat_file='race_stats.txt', x=0, y=0, selected=False, font_color=(0,0,0), font_bg=(159, 182, 205), border_color=(50,50,50), border_selected=(255,255,0)):
		#icon = pygame.image.load(os.path.join(GFXDIR, "test_icon.png"))
		self.race_name = race_name
		self.sprite_file = sprite_file
		self.stat_file = stat_file

		self.selected_hair = 0
		self.hairs = [None, 'a', 'b', 'c', 'd', 'e', 'f', 'i', 'j']
		self.selected_race = 0
		self.races = ['Longear', 'Ghost', 'Croco', 'Human', 'Human2', 'Devil', 'Human3', 'Elf', 'Alien', 'WhiteGuy', 'Medusa', 'Dragon', 'Taurus', 'Squid', 'GreyGuy', 'Imhotep', 'Wolf']
		self.selected_class = 0
		self.classes = ['Hunter', 'Healer', 'Chuck Norris']

		self.surface = surface
		self.x = x
		self.y = y
		self.images = []
		self.load_tiles()
		self.child_buttons = []
		self.parent_button = Func_Button(x, y, self.race_tile.rect.width + 80, self.race_tile.rect.height + 20, 2, (200, 200, 200), (50, 50, 50), (150, 150, 150), None, self.images, 20, self.surface, self.toggle_visibility_buttons, True, False, False)
		#Adding hideable buttons
		self.child_buttons.append(Func_Button(x, y-25, self.race_tile.rect.width + 80, 20, 2, (200, 200, 200), (50, 50, 50), (150, 150, 150), [["Equip", None]], None, 20, self.surface, self.button_click, False, False, True))
		self.child_buttons.append(Func_Button(x, y+self.race_tile.rect.height+25, self.race_tile.rect.width + 80, 20, 2, (200, 200, 200), (50, 50, 50), (150, 150, 150), [["Sell", None]], None, 20, self.surface, self.button_click, False, False, True))
		#Adding static buttons
		self.child_buttons.append(Func_Button(x+8, y+10, 18, 18, 1, (200, 200, 200), (50, 50, 50), (150, 150, 150), [["<", None]], None, 20, self.surface, self.prev_hair, True, False, False))
		self.child_buttons.append(Func_Button(x+self.race_tile.rect.width+52, y+10, 18, 18, 1, (200, 200, 200), (50, 50, 50), (150, 150, 150), [[">", None]], None, 20, self.surface, self.next_hair, True, False, False))

		self.child_buttons.append(Func_Button(x+8, y+35, 18, 18, 1, (200, 200, 200), (50, 50, 50), (150, 150, 150), [["<", None]], None, 20, self.surface, self.prev_race, True, False, False))
		self.child_buttons.append(Func_Button(x+self.race_tile.rect.width+52, y+35, 18, 18, 1, (200, 200, 200), (50, 50, 50), (150, 150, 150), [[">", None]], None, 20, self.surface, self.next_race, True, False, False))

		self.child_buttons.append(Func_Button(x+8, y+60, 18, 18, 1, (200, 200, 200), (50, 50, 50), (150, 150, 150), [["<", None]], None, 20, self.surface, self.prev_class, True, False, False))
		self.child_buttons.append(Func_Button(x+self.race_tile.rect.width+52, y+60, 18, 18, 1, (200, 200, 200), (50, 50, 50), (150, 150, 150), [[">", None]], None, 20, self.surface, self.next_class, True, False, False))

	def load_tiles(self):
		self.race_tile = race_tile(self.races[self.selected_race]).get_tile(self.x, self.y, '270')
		if self.hairs[self.selected_hair] != None:
			self.hair_tile = hair_tile(self.races[self.selected_race], self.hairs[self.selected_hair]).get_tile(self.x, self.y, '270')
			self.images = [[self.race_tile, (40, 0)], [self.hair_tile, (40, 0)]]
		else: self.images = [[self.race_tile, (40, 0)]]

	def update_tiles(self):
		self.race_tile = race_tile(self.races[self.selected_race]).get_tile(self.x, self.y, '270')
		if self.hairs[self.selected_hair] != None:
			self.hair_tile = hair_tile(self.races[self.selected_race], self.hairs[self.selected_hair]).get_tile(self.x, self.y, '270')
			self.parent_button.images = [[self.race_tile, (40, 0)], [self.hair_tile, (40, 0)]]
		else: self.parent_button.images = [[self.race_tile, (40, 0)]]
	
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
		
	def toggle_visibility_buttons(self):
		for b in self.child_buttons:
			print 'In enable_buttons:', b, b.hideable
			if b.hideable:
				b.toggle_visibility()

	def next_hair(self):
		print "Next hair selected"
		self.selected_hair = (self.selected_hair + 1) % len(self.hairs)

	def prev_hair(self):
		print "Previous hair selected"
		self.selected_hair = (self.selected_hair - 1) % len(self.hairs)

	def next_race(self):
		print "Next race selected"
		self.selected_race = (self.selected_race + 1) % len(self.races)

	def prev_race(self):
		print "Previous race selected"
		self.selected_race = (self.selected_race - 1) % len(self.races)

	def next_class(self):
		print "Next class selected"
		self.selected_class = (self.selected_class + 1) % len(self.classes)

	def prev_class(self):
		print "Previous class selected"
		self.selected_class = (self.selected_class - 1) % len(self.classes)
			
class race_preview:
	def __init__(self, race_name, hair_name = None, race_sprite_file='race_sprites.txt', hair_sprite_file='hair_sprites.txt', stat_file='race_stats.txt', x=0, y=0, selected=False, font_color=(0,0,0), font_bg=(159, 182, 205), border_color=(50,50,50), border_selected=(255,255,0)):
		self.race_name = race_name
		self.hair_name = hair_name
		self.race_sprite_file = race_sprite_file
		self.hair_sprite_file = hair_sprite_file
		self.stat_file = stat_file
		self.x = x
		self.y = y
		self.font_color = font_color
		self.font_bg = font_bg
		self.border_color = border_color
		self.border_selected = border_selected
		self.selected = selected
		self.load_tiles()
		self.load_text()
		self.load_box()
	
	def contains(self, x, y):
		return self.box.contains(x, y)
		
	def select(self):
		self.box.select()
		
	def unselect(self):
		self.box.unselect()
		
	def toggle(self):
		self.box.toggle()
		
	def load_tiles(self):
		self.race_tile = race_tile(self.race_name).get_tile(self.x, self.y, '270')
		self.hair_tile = hair_tile(self.race_name, self.hair_name).get_tile(self.x, self.y, '270')
	
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
		
	def load_box(self):
		self.box = info_box([self.race_tile, self.hair_tile], self.race_stats[self.race_name], self.x, self.y, self.selected, self.font_color, self.font_bg, self.border_color, self.border_selected)
	
	def draw(self, surface):
		self.box.draw_box(surface)
		
class info_box:
	def __init__(self, tiles, texts, x=0, y=0, selected=False, font_color=(0,0,0), font_bg=(159, 182, 205), border_color_unselected=(50,50,50), border_color_selected=(255,255,255)):
		self.tiles = tiles
		self.texts = texts
		self.x = x
		self.y = y
		self.font_color = font_color
		self.font_bg = font_bg
		self.border_color_unselected = border_color_unselected
		self.border_color_selected = border_color_selected
		self.border_color = border_color_unselected
		self.selected = selected
		
		#self.sprites = pygame.sprite.LayeredUpdates()
		#self.sprites.add(self.sprite)
		
		self.infofont = pygame.font.Font(FONT, int(20*FONTSCALE))
		self.infotext = []
		self.inforect = []
		self.max_width = 0
		tiles_height = 0
		for t in self.tiles:
			if t.rect.height > tiles_height:
				tiles_height = t.rect.height
		
		for i in range(len(self.texts)):
			text = self.texts[i]
			self.temptext = self.infofont.render(text[0] + ': ' + str(text[1]), True, self.font_color, self.font_bg)
			self.temprect = self.temptext.get_rect()
			self.temprect.x = self.x
			self.temprect.y = self.y + tiles_height + (i*15)
			if self.temprect.width > self.max_width:
				self.max_width = self.temprect.width
			
			self.infotext.append(self.temptext)
			self.inforect.append(self.temprect)

		self.border = pygame.Surface((self.max_width + 8, (len(self.texts))*15 + 69))
		self.border.fill(self.border_color)
		self.borderrect = self.border.get_rect()
		self.borderrect.x = self.x
		self.borderrect.y = self.y
		
		self.background = pygame.Surface((self.max_width + 4, (len(self.texts))*15 + 65))
		self.background.fill(self.font_bg)
		self.bgrect = self.background.get_rect()
		self.bgrect.x = self.x + 2
		self.bgrect.y = self.y + 2
		
		for t in self.tiles:
			t.rect.centerx = self.bgrect.centerx
		
		for r in self.inforect:
			r.centerx = self.bgrect.centerx
		
	def contains(self, x, y):
		return x >= self.x and y >= self.y and x < self.x + self.borderrect.width and y < self.y + self.borderrect.height
		
	def select(self):
		self.selected = True
		self.border.fill(self.border_color_selected)
		
	def unselect(self):
		self.selected = False
		self.border.fill(self.border_color_unselected)
		
	def toggle(self):
		if self.selected:
			self.unselect()
		else: 
			self.select()
		
	def draw_box(self, screen):
		screen.blit(self.border, self.borderrect)
		screen.blit(self.background, self.bgrect)
		for t in self.tiles:
			screen.blit(t.image, t.rect)
		#self.sprites.draw(screen)
		for i in range(len(self.infotext)):
			screen.blit(self.infotext[i], self.inforect[i])

class race_tile:
	def load_races(self, race_sprite_file):
		path = os.path.join(GFXDIR, race_sprite_file)
		f = open(path, 'r')
		
		self.races = {}
		# iterate over the lines in the file
		for line in f:
			# split the line into a list of column values
			columns = line.split(',')
			# clean any whitespace off the items
			columns = [col.strip() for col in columns]
			self.races[columns[0]] = [columns[1], columns[2]]
			
		f.close()

	def load_characters(self, filename):
		#chars1 = load_tiles('sprite_collection.png', CHAR_SIZE, (255, 0, 255), SCALE)
		#chars2 = load_tiles('sprite_collection_2.png', CHAR_SIZE, (255, 0, 255), SCALE)
		
		chars = load_tiles(filename, CHAR_SIZE, (255, 0, 255), SCALE)

		self.charnames = []
		self.chartypes = {}
		for i, char in enumerate(chars):
			name = 'char' + str(i+1)
			self.charnames.append(name)
			self.chartypes[name + '_270'] = char[0]
			self.chartypes[name + '_180'] = char[1]
			self.chartypes[name + '_0'] = char[2]
			self.chartypes[name + '_90'] = char[3]
	
	def __init__(self, race):
		self.race = race
		self.sprites = pygame.sprite.LayeredUpdates()
		
		self.load_races('race_sprites.txt')
		#races = {'longear': ['sprite_collection.png', '1']}

		temp = self.races[race]
		self.path = temp[0]
		self.place = 'char' + temp[1]

		self.load_characters(self.path)

	def get_sprites(self, x=0, y=0):
		self.sprites = pygame.sprite.LayeredUpdates()
		tiles = [self.chartypes[self.place + '_' + str(0)] , self.chartypes[self.place + '_' + str(90)], self.chartypes[self.place + '_' + str(180)], self.chartypes[self.place + '_' + str(270)]]
		for i in range(len(tiles)):
			self.sprites.add(Tile(tiles[i], pygame.Rect(x+(48*i)+TILE_SIZE[0], y+TILE_SIZE[1], *TILE_SIZE), layer = 0))
		return self.sprites

	def get_sprite(self, x=0, y=0, orientation=270):
		self.sprites = pygame.sprite.LayeredUpdates()
		print TILE_SIZE
		self.sprites.add(Tile(self.chartypes[self.place + '_' + str(orientation)], pygame.Rect(x, y, *TILE_SIZE), layer = 0))
		return self.sprites
		
	def get_tile(self, x=0, y=0, orientation=270):
		return Tile(self.chartypes[self.place + '_' + str(orientation)], pygame.Rect(x, y, *CHAR_SIZE), layer = 0)

class hair_tile:
	def load_hairs(self, hair_sprite_file):
		path = os.path.join(GFXDIR, hair_sprite_file)
		f = open(path, 'r')
		
		self.hairs = {}
		# iterate over the lines in the file
		for line in f:
			# split the line into a list of column values
			columns = line.split(',')
			# clean any whitespace off the items
			columns = [col.strip() for col in columns]
			self.hairs[columns[0]] = [columns[1], columns[2]]
		f.close()

	def load_hair_sprites(self, filename):
		#chars1 = load_tiles('sprite_collection.png', CHAR_SIZE, (255, 0, 255), SCALE)
		#chars2 = load_tiles('sprite_collection_2.png', CHAR_SIZE, (255, 0, 255), SCALE)
		
		hairs = load_tiles(filename, HAIR_SIZE, (255, 0, 255), SCALE)

		self.hairnames = []
		self.hairtypes = {}
		for i, hair in enumerate(hairs):
			name = 'hair' + str(i+1)
			self.hairnames.append(name)
			self.hairtypes[name + '_270'] = hair[0]
			self.hairtypes[name + '_180'] = hair[1]
			self.hairtypes[name + '_0'] = hair[2]
			self.hairtypes[name + '_90'] = pygame.transform.flip(hair[1], True, False)

	def load_compatible_hairs(self, race, race_hair_file):
		path = os.path.join(GFXDIR, race_hair_file)
		f = open(path, 'r')
		
		self.race_hairs = {}
		# iterate over the lines in the file
		for line in f:
			# split the line into a list of column values
			columns = line.split(',')
			# clean any whitespace off the items
			columns = [col.strip() for col in columns]
			races = []
			for r in range(1, len(columns)):
				temp = columns[r].split(';')
				temp = [col.strip() for col in temp]
				races.append(temp)
			self.race_hairs[columns[0]] = races
		f.close()
	
	def set_hair_height(self):
		self.hair_height = 0
		for r in self.race_hairs[self.hairtype]:
			if r[0] == self.race:
				self.hair_height = int(r[1])
				print self.hair_height
	
	def __init__(self, race, hairtype):
		self.race = race
		self.hairtype = hairtype
		self.sprites = pygame.sprite.LayeredUpdates()
		
		self.load_hairs('hair_sprites.txt')
		self.load_compatible_hairs(self.race, 'race_hairs.txt')
		#races = {'longear': ['sprite_collection.png', '1']}
		
		temp = self.hairs[hairtype]
		self.path = temp[0]
		self.place = 'hair' + temp[1]

		self.load_hair_sprites(self.path)
		
	def get_tile(self, x=0, y=0, orientation=270, layer=0):
		self.set_hair_height()
		y = y + self.hair_height
		print y
		return Tile(self.hairtypes[self.place + '_' + str(orientation)], pygame.Rect(x, y, *HAIR_SIZE), layer)

class Tile(pygame.sprite.Sprite):
	def __init__(self, image, rect=None, layer=0):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = image.get_rect()
		self._layer = layer
		if rect is not None:
			self.rect = rect

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
		self.buttonfont = pygame.font.Font(FONT, int(fontsize*FONTSCALE))
		self.buttontext = self.buttonfont.render(text, True, (0, 0, 0), (159, 182, 205))
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
	win = CharTest()
	win.loop()

