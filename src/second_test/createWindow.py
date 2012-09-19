import os, sys, time
import pygame
from pygame.locals import *
from helpers import *

if not pygame.font: print "Warning: Fonts not enabled"
if not pygame.mixer: print "Warning: Audio not enabled"

SIZE = int(sys.argv[1])

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
		w = 'w'
		l = 'l'
		self.map = background_map([
				[w,w,w,w,w,w,w,w,w,w,w,w,w,w,w,w,w,w,w,w],
				[w,w,w,w,w,w,w,w,w,w,w,w,w,w,w,w,w,w,w,w],
                                [w,w,w,w,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l],
                                [w,w,w,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l],
                                [w,w,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l],
                                [w,w,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l],
                                [w,w,l,l,l,l,l,l,l,l,l,w,w,w,w,w,w,w,l,l],
                                [w,w,l,l,l,l,l,l,l,l,w,w,w,w,w,w,w,w,w,l],
                                [w,w,l,l,l,l,l,l,l,w,w,w,l,l,l,l,l,w,w,w],
                                [w,w,l,l,l,l,l,l,l,w,w,w,l,l,l,l,l,w,w,w],
                                [w,w,l,l,l,l,l,l,l,l,w,w,w,l,l,l,w,w,w,w],
                                [w,w,l,l,l,l,l,l,l,l,l,w,w,w,w,w,w,w,w,w],
                                [w,w,l,l,l,l,l,l,l,l,l,l,l,l,w,w,w,w,w,l],
                                [w,w,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l],
                                [w,w,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l,l],
				], 20, 15)
		self.player1 = player([
					['b', 4, 3]
				])
		self.grid_sprites = pygame.sprite.Group()
		self.map_sprites = self.map.get_sprites()
		self.player_sprites = self.player1.get_sprites()

	def click(self):
		characters = self.player1.get_characters()
		for i in range(len(characters)):
			char_coords = characters[i].get_coords()
			mouse_coords = list(pygame.mouse.get_pos())
			mouse_coords = [mouse_coords[0]/SIZE, mouse_coords[1]/SIZE]
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
	#print "Loading opaquegrid"
	#print coords
	def __init__(self, grid, coords):
		self.sprites = pygame.sprite.Group()
		for i in range(len(grid)):
			self.sprites.add(opaque_grid(pygame.Rect(grid[i][0]*SIZE, grid[i][1]*SIZE, SIZE, SIZE)))

	def get_sprites(self):
		return self.sprites

class background_map:
	# Map class to create the background layer, holds any static and dynamical elements in the field.
	
	def __init__(self, map, height, width):
                self.width = width
                self.height = height
		self.map = map
		self.sprites = pygame.sprite.Group()
		for x in range(self.width):
			for y in range(self.height):
				if map[x][y] == 'w':
					print "Water at: (" + str(x) + "," + str(y) + ")"
					self.sprites.add(water(pygame.Rect(y*SIZE, x*SIZE, SIZE, SIZE)))
				elif map[x][y] == 'l':
					print "Land at: (" + str(x) + "," + str(y) + ")"
					self.sprites.add(land(pygame.Rect(y*SIZE, x*SIZE, SIZE, SIZE)))
	def get_sprites(self):
		return self.sprites

class player:
	# Class to create player or team in the game. One player may have many characters.

	def __init__(self, coords):
		self.coords = coords
		self.sprites = pygame.sprite.Group()
		self.characters = []
		for i in range(len(coords)):
			if coords[i][0] == 'b':
				x = coords[i][1]
				y = coords[i][2]
				print "Player1, ball sprite at: (" + str(x) + "," + str(y) + ")"
				self.sprites.add(ball(pygame.Rect(y*SIZE, x*SIZE, SIZE, SIZE)))
				self.characters.append(character(2, [y, x], 90))
	def get_sprites(self):
		return self.sprites
	
	def get_characters(self):
		return self.characters

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
			self.sprites.add(ball(pygame.Rect(coords[0]*SIZE, coords[1]*SIZE, SIZE, SIZE)))

class character:
	# Universal class for any character in the game

	def __init__(self, movement, coords, heading):
		self.movement = movement	# Movement points left
		self.coords = coords 		# Array of x and y
		self.heading = heading		# Angle from north in degrees, possible values are: 0, 45, 90, 135, 180, 225, 270 and 315
		self.selected = False
	
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
		#movement_grid = self.get_surroundings(self.coords)
		movement_grid = []
		if self.movement > 1:
			for i in range(1, (self.movement + 1)):
				"""
				for i in range(len(movement_grid)):
					temp_grid = self.get_surroundings(movement_grid[i])
					movement_grid.extend(temp_grid)
				"""
				movement_grid.append([self.coords[0] + i, self.coords[1]])
				movement_grid.append([self.coords[0] + i, self.coords[1] + i])
				movement_grid.append([self.coords[0], self.coords[1] + i])
				movement_grid.append([self.coords[0] - i, self.coords[1] + i])
				movement_grid.append([self.coords[0] - i, self.coords[1]])
				movement_grid.append([self.coords[0] - i, self.coords[1] - i])
				movement_grid.append([self.coords[0] + i, self.coords[1] - i])
				movement_grid.append([self.coords[0], self.coords[1] - i])
		for k in range(len(movement_grid)):
			#for j in range(len(movementGrid[k])):
			print movement_grid[k]
		return movement_grid

	def get_surroundings(self, coords):
		return_grid = []
		print coords
		for x in range(0, 3):
			for y in range(0, 3):
				if (coords[0] - x) >= 0:
					if (coords[1] - y) >= 0:
						return_grid.append([x,y])
		return return_grid	

	def is_legal_move(self, coords):
		movement_grid = self.get_movement_grid()
		for i in range(len(movement_grid)):
			if coords == movement_grid[i]:
				return True
		return False

# Following classes define the graphical elements, or Sprites.

class land(pygame.sprite.Sprite):
        
    def __init__(self, rect=None):
        pygame.sprite.Sprite.__init__(self) 
        self.image, self.rect = load_image('land24.jpg', None, SIZE/24)
        if rect != None:
            self.rect = rect

class water(pygame.sprite.Sprite):

    def __init__(self, rect=None):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('water24.jpg', None, SIZE/24)
        if rect != None:
            self.rect = rect

class ball(pygame.sprite.Sprite):

   def __init__(self, rect=None):
	pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('player.png', None, SIZE/24)
        if rect != None:
            self.rect = rect

class opaque_grid(pygame.sprite.Sprite):

   def __init__(self, rect=None):
	pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('grid.png', None, SIZE/24)
        if rect != None:
            self.rect = rect

# Main starts here

if __name__ == "__main__":
	main_window = xadir_main()
	main_window.main_loop()
