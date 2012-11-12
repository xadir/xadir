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
		"""
		self.load_characters('sprite_collection.png')
		print self.charnames

		self.sprites = pygame.sprite.LayeredUpdates()
		tile = self.chartypes[self.charnames[0] + '_' + '270']
		self.sprites.add(Tile(tile, pygame.Rect(TILE_SIZE[0], TILE_SIZE[1], *TILE_SIZE), layer = 0))
		"""

		self.sprites = pygame.sprite.LayeredUpdates()
		self.sprites.add(race_sprite('Longear').get_sprite(0, 0, '270'))
		self.sprites.add(race_sprite('Ghost').get_sprite(0, 60, '270'))
		self.sprites.add(race_sprite('Croco').get_sprite(0, 120, '270'))
		self.sprites.add(race_sprite('Longear').get_sprites(0, 200))
		self.sprites.add(race_sprite('Ghost').get_sprites(0, 260))
		self.sprites.add(race_sprite('Croco').get_sprites(0, 320))
		
		self.preview_sprite = race_sprite('Longear').get_sprite(0, 400, '270')
		self.preview_sprite2 = race_sprite('Ghost').get_sprite(100, 400, '270')
		self.preview_info = [('Health', 100), ('Attack', 100), ('Defence', 50)]
		self.preview_info2 = [('Health', 100), ('Attack', 100), ('Defence', 50), ('Dexterity', 20)]
		
		self.preview = race_preview(self.preview_sprite, self.preview_info, 0, 400, (0, 0, 0), (150, 150, 150))
		self.preview2 = race_preview(self.preview_sprite2, self.preview_info2, 100, 400, (0, 0, 0), (150, 150, 150))


	def loop(self):

		while 1:
			self.screen.fill((127, 127, 127))
			self.sprites.draw(self.screen)
			self.preview.draw_preview(self.screen)
			self.preview2.draw_preview(self.screen)
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

			time.sleep(0.05)
			
class race_preview:
	def __init__(self, sprite, text, x=0, y=0, font_color=(0,0,0), font_bg=(159, 182, 205)):
		self.sprite = sprite
		self.text = text
		self.x = x
		self.y = y
		self.font_color = font_color
		self.font_bg = font_bg
		
		self.sprites = pygame.sprite.LayeredUpdates()
		self.sprites.add(self.sprite)
		
		self.infofont = pygame.font.Font(FONT, int(20*FONTSCALE))
		self.infotext = []
		self.inforect = []
		self.max_width = 0
		
		for i in range(len(self.text)):
			text = self.text[i]
			self.temptext = self.infofont.render(text[0] + ': ' + str(text[1]), True, self.font_color, self.font_bg)
			self.temprect = self.temptext.get_rect()
			self.temprect.centerx = self.x + 70
			self.temprect.top = self.y + 110 + (i*15)
			if self.temprect.width > self.max_width:
				self.max_width = self.temprect.width
			
			self.infotext.append(self.temptext)
			self.inforect.append(self.temprect)

		self.border = pygame.Surface((self.max_width + 8, (len(self.text))*15 + 69))
		self.border.fill((50,50,50))
		self.borderrect = self.border.get_rect()
		self.borderrect.centerx = self.x + 70
		self.borderrect.top = self.y + 48
		
		self.background = pygame.Surface((self.max_width + 4, (len(self.text))*15 + 65))
		self.background.fill(self.font_bg)
		self.bgrect = self.background.get_rect()
		self.bgrect.centerx = self.x + 70
		self.bgrect.top = self.y + 50
		
	def draw_preview(self, screen):
		screen.blit(self.border, self.borderrect)
		screen.blit(self.background, self.bgrect)
		self.sprites.draw(screen)
		for i in range(len(self.infotext)):
			screen.blit(self.infotext[i], self.inforect[i])

class race_sprite:
	def load_races(self, conf_file):
		path = os.path.join(GFXDIR, 'race_sprites.txt')
		f = open(path, 'r')
		
		self.races = {}
		# iterate over the lines in the file
		for line in f:
			# split the line into a list of column values
			columns = line.split(',')
			# clean any whitespace off the items
			columns = [col.strip() for col in columns]
			self.races[columns[0]] = [columns[1], columns[2]]

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
		self.sprites.add(Tile(self.chartypes[self.place + '_' + str(orientation)], pygame.Rect(x+TILE_SIZE[0], y+TILE_SIZE[1], *TILE_SIZE), layer = 0))
		return self.sprites


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

