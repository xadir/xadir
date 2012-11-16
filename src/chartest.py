import sys, time
import pygame
from resources import *
from grid import *
from algo import *

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
		self.preview.append(race_preview(race_name = 'Longear', x = 0, y = 0))
		#self.preview.append(race_preview(race_name = 'Longear', x = 100, y = 0))
		self.preview.append(race_preview(race_name = 'Croco', x = 100, y = 0))
		self.preview.append(race_preview(race_name = 'Human', x = 200, y = 0))
		self.preview.append(race_preview(race_name = 'Dragon', x = 300, y = 0))


	def loop(self):

		while 1:
			self.screen.fill((127, 127, 127))
			for i in range(len(self.preview)):
				self.preview[i].draw(self.screen)
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						for p in self.preview:
							if p.contains(*event.pos):
								p.toggle()
				elif event.type == pygame.QUIT:
					sys.exit()

			time.sleep(0.05)
			
class race_preview:
	def __init__(self, race_name, sprite_file='race_sprites.txt', stat_file='race_stats.txt', x=0, y=0, selected=False, font_color=(0,0,0), font_bg=(159, 182, 205), border_color=(50,50,50), border_selected=(255,255,0)):
		self.race_name = race_name
		self.sprite_file = sprite_file
		self.stat_file = stat_file
		self.x = x
		self.y = y
		self.font_color = font_color
		self.font_bg = font_bg
		self.border_color = border_color
		self.border_selected = border_selected
		self.selected = selected
		self.load_tile()
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
		
	def load_box(self):
		self.box = info_box(self.race_tile, self.race_stats[self.race_name], self.x, self.y, self.selected, self.font_color, self.font_bg, self.border_color, self.border_selected)
	
	def draw(self, surface):
		self.box.draw_box(surface)
		
class info_box:
	def __init__(self, tile, text, x=0, y=0, selected=False, font_color=(0,0,0), font_bg=(159, 182, 205), border_color_unselected=(50,50,50), border_color_selected=(255,255,255)):
		self.tile = tile
		self.text = text
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
		
		for i in range(len(self.text)):
			text = self.text[i]
			self.temptext = self.infofont.render(text[0] + ': ' + str(text[1]), True, self.font_color, self.font_bg)
			self.temprect = self.temptext.get_rect()
			self.temprect.x = self.x
			self.temprect.y = self.y + self.tile.rect.height + (i*15)
			if self.temprect.width > self.max_width:
				self.max_width = self.temprect.width
			
			self.infotext.append(self.temptext)
			self.inforect.append(self.temprect)

		self.border = pygame.Surface((self.max_width + 8, (len(self.text))*15 + 69))
		self.border.fill(self.border_color)
		self.borderrect = self.border.get_rect()
		self.borderrect.x = self.x
		self.borderrect.y = self.y
		
		self.background = pygame.Surface((self.max_width + 4, (len(self.text))*15 + 65))
		self.background.fill(self.font_bg)
		self.bgrect = self.background.get_rect()
		self.bgrect.x = self.x + 2
		self.bgrect.y = self.y + 2
		
		self.tile.rect.centerx = self.bgrect.centerx
		
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
		screen.blit(self.tile.image, self.tile.rect)
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


class Tile(pygame.sprite.Sprite):
	def __init__(self, image, rect=None, layer=0):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = image.get_rect()
		self._layer = layer
		if rect is not None:
			self.rect = rect

if __name__ == "__main__":
	win = CharTest()
	win.loop()

