import os, sys, time
import pygame
import numpy
from pygame.locals import *
from resources import *

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer: 
	print "Warning: Audio not enabled"

class xadir_main:
	# Main class for initialization and mechanics of the game
	
	def __init__(self, width=1200, height=720):
		pygame.init()
		self.width = width
		self.height = height
		self.screen = pygame.display.set_mode((self.width, self.height))

	def main_loop(self):
		self.load_sprites()
		while 1:
			self.map_sprites.draw(self.screen)
			self.player_sprites.draw(self.screen)
			self.grid_sprites.draw(self.screen)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					self.click()
			pygame.display.flip()
			self.update_sprites()
			time.sleep(0.05)

	def load_sprites(self):
    		"""Load the sprites that we need"""
		self.walkable = ['l']
		self.map = background_map([
				['w','w','w','w','w','w','w','w','w','w','w','w','w','w','w','w','w','w','w','w'],
				['w','w','w','w','w','w','w','w','w','w','w','w','w','w','w','w','w','w','w','w'],
                                ['w','w','w','w','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l'],
                                ['w','w','w','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l'],
                                ['w','w','w','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l'],
                                ['w','w','w','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l'],
                                ['w','w','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l'],
                                ['w','w','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l','l'],
                                ['w','w','l','l','l','l','l','l','l','l','l','w','l','l','l','l','l','l','l','l'],
                                ['w','w','l','l','l','l','l','l','l','l','w','w','w','l','l','l','l','l','l','l'],
                                ['w','w','l','l','l','l','l','l','l','l','w','w','w','l','l','l','l','l','l','l'],
                                ['w','w','l','l','l','l','l','l','l','l','w','w','w','l','l','l','l','l','l','l'],
                                ['w','w','l','l','l','l','l','l','l','l','w','w','w','l','l','l','l','l','l','l'],
                                ['w','w','l','l','l','l','l','l','l','l','w','w','w','l','l','l','l','l','l','l'],
                                ['w','w','l','l','l','l','l','l','l','l','w','w','w','l','l','l','l','l','l','l'],
				], 20, 15)
		self.player1 = player([['b', 4, 3]], self)
		self.grid_sprites = pygame.sprite.Group()
		self.map_sprites = self.map.get_sprites()
		self.player_sprites = self.player1.get_sprites()

	def click(self):
		characters = self.player1.get_characters()
		for i in range(len(characters)):
			char_coords = characters[i].get_coords()
			mouse_coords = list(pygame.mouse.get_pos())
			mouse_coords = [mouse_coords[0]/TILE_SIZE[0], mouse_coords[1]/TILE_SIZE[1]]
			print char_coords
			print mouse_coords
			if char_coords == mouse_coords:
				print "Clicked on character"
				if characters[i].is_selected():
					characters[i].unselect()
					self.grid_sprites = pygame.sprite.Group()
				else:
					characters[i].select()
					self.movement_grid = sprite_grid(characters[i].get_movement_grid(), characters[i].get_coords())
					self.grid_sprites = self.movement_grid.get_sprites()			
			elif characters[i].is_selected():
				if characters[i].is_legal_move(mouse_coords):
					characters[i].set_coords(mouse_coords)
					self.grid_sprites = pygame.sprite.Group()
					characters[i].unselect
			if char_coords != mouse_coords:
				characters[i].unselect()
	def update_sprites(self):
		self.player1.update_sprites()
		self.player_sprites = self.player1.get_sprites()

class sprite_grid:
	def __init__(self, grid, coords):
		self.sprites = pygame.sprite.Group()
		for i in range(len(grid)):
			tile = tiletypes['g']
			self.sprites.add(Tile(tile, pygame.Rect(grid[i][0]*TILE_SIZE[0], grid[i][1]*TILE_SIZE[1], *TILE_SIZE)))

	def get_sprites(self):
		return self.sprites

class background_map:
	# Map class to create the background layer, holds any static and dynamical elements in the field.
	
	def __init__(self, map, width, height):
                self.width = width
                self.height = height
		self.map = map
		self.sprites = pygame.sprite.Group()
		for y in range(self.height):
			for x in range(self.width):
				tiletype = self.map[y][x]
				tile = tiletypes[tiletype]
				#print x, y
				self.sprites.add(Tile(tile, pygame.Rect(x*TILE_SIZE[0], y*TILE_SIZE[1], *TILE_SIZE)))
		"""
		for x in range(self.width):
			for y in range(self.height):
				if map[x][y] == 'w':
					#print "Water at: (" + str(x) + "," + str(y) + ")"
					self.sprites.add(water(pygame.Rect(y*SIZE3, x*SIZE3, SIZE3, SIZE3)))
				elif map[x][y] == 'l':
					#print "Land at: (" + str(x) + "," + str(y) + ")"
					self.sprites.add(land(pygame.Rect(y*SIZE3, x*SIZE3, SIZE3, SIZE3)))
		"""	
	def get_sprites(self):
		return self.sprites

	def get_map(self):
		return self.map

class player:
	# Class to create player or team in the game. One player may have many characters.

	def __init__(self, coords, main):
		self.main = main
		self.coords = coords
		self.sprites = pygame.sprite.Group()
		self.characters = []
		for i in range(len(coords)):
			character_type = coords[i][0]
			y = coords[i][1]
			x = coords[i][2]
			tile = tiletypes[character_type]
			self.sprites.add(Tile(tile, pygame.Rect(x*TILE_SIZE[0], y*TILE_SIZE[1], *TILE_SIZE)))
			self.characters.append(character(character_type, 2, [y, x], 90, self.main))

	def get_sprites(self):
		return self.sprites
	
	def get_characters(self):
		return self.characters

	def get_characters_coords(self):
		coords = []		
		for i in self.characters:
			coords.append(self.characters[i].coords)
		return coords

	def select_character(self, character):
		self.characters[character].select()

	def unselect_character(self, character):
		self.characters[character].unselect()

	def character_is_selected(self, character):
		return self.characters[character].is_selected()
	
	def update_sprites(self):
		self.sprites = pygame.sprite.Group()
		for i in range(len(self.characters)):
			coords = self.characters[i].get_coords()
			character_type = self.characters[i].get_type()
			tile = tiletypes[character_type]
			self.sprites.add(Tile(tile, pygame.Rect(coords[0]*TILE_SIZE[0], coords[1]*TILE_SIZE[1], *TILE_SIZE)))

class character:
	# Universal class for any character in the game

	def __init__(self, character_type, movement, coords, heading, main):
		self.type = character_type		
		self.movement = movement	# Movement points left
		self.coords = coords 		# Array of x and y
		self.heading = heading		# Angle from north in degrees, possible values are: 0, 45, 90, 135, 180, 225, 270 and 315
		self.selected = False
		self.background_map = main.map.get_map()
		self.walkable_tiles = main.walkable
		
	def get_type(self):
		return self.type

	def set_type(self, character_type):
		self.type = character_type

	def get_coords(self):			# Returns coordinates of the character, return is array [x, y]
		return self.coords
	
	def set_coords(self, coords):			# Sets coordinates of characte, input is array of [x, y]
		self.coords = coords

	def get_heading(self):			# Returns heading of character in degrees
		return self.heading

	def set_heading(self, angle):			# Sets the absolute heading of character
		self.heading = angle
	
	def is_selected(self):
		return self.selected
	
	def select(self):
		self.selected = True
	
	def unselect(self):
		self.selected = False
	
	def turn(self, angle):			# Turns character given amount, relative to previous heading. For now only turns 90-degrees at a time
		angle = angle % 360
		if angle <= 45:
			self.heading = (self.heading + angle) % 360
		elif angle <= 90:
			self.heading = (self.heading + angle) % 360
		elif angle <= 135:
			self.heading = (self.heading + angle) % 360

	def move_forward(self, steps):		# Moves to headed direction given amount of steps
		if self.movement <= steps:
			if self.heading == 0:
				self.coords[1] -= steps
			elif self.heading == 90:
				self.coords[0] += steps
			elif self.heading == 180:
				self.coords[1] += steps
			elif self.heading == 270:
				self.coords[0] -= steps
	
	def get_movement_grid(self):			# Return grid of available cells to move to		
		movement_grid = self.get_surroundings(self.coords)
		if self.movement > 1:
			for i in range(2, (self.movement + 1)):
				for i in range(len(movement_grid)):
					movement_grid.extend(self.get_surroundings(movement_grid[i]))
		movement_grid = [list(x) for x in set(tuple(x) for x in movement_grid)]
		return movement_grid		

	def get_surroundings(self, coords):		# Return surrounding tiles that are walkable
		return_grid = []
		for x in range(-1, 2):
			for y in range(-1, 2):
				temp_coords = [coords[0] + x, coords[1] + y]
				print temp_coords
				if self.is_walkable_tile(temp_coords): return_grid.append(temp_coords)
		return return_grid

	def is_walkable_tile(self, coords):		# To check if tile is walkable
		if coords[1] >= 15: return False
		if coords[0] >= 20: return False
		if coords[0] < 0: return False
		if coords[1] < 0: return False

		for w in self.walkable_tiles:
			if self.background_map[coords[1]][coords[0]] == w:
				return True
		return False

	def is_legal_move(self, coords):		# Before moving, check if target is inside movement grid
		movement_grid = self.get_movement_grid()
		for i in range(len(movement_grid)):
			if coords == movement_grid[i]:
				return True
		return False

# Following classes define the graphical elements, or Sprites.

class Tile(pygame.sprite.Sprite):
	def __init__(self, image, rect=None):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = image.get_rect()
		if rect is not None:
			self.rect = rect

SCALE = 3
ORIG_TILE_SIZE = (16, 16)
TILE_SIZE = (ORIG_TILE_SIZE[0]*SCALE, ORIG_TILE_SIZE[1]*SCALE)
TILEGROUP_SIZE = (3 * ORIG_TILE_SIZE[0], 3 * ORIG_TILE_SIZE[1])


if __name__ == "__main__":
	game = xadir_main()

	tiles = load_tiles('placeholder_tilemap.png', TILEGROUP_SIZE, (255, 0, 255), SCALE)
	waters = parse_tiles(tiles[0][0], TILE_SIZE)
	lands = parse_tiles(tiles[0][1], TILE_SIZE)
	#characters = parse_tiles(tiles[1][2], TILE_SIZE)
	

	tiletypes = {
		'l': lands[1][1],
		'w': waters[1][1],
		'b': lands[0][0],
		'g': lands[1][0]
	}

	game.main_loop()
