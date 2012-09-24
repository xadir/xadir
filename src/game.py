import os, sys, time
import pygame
import numpy
import math
import random
from pygame.locals import *
from resources import *

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

class xadir_main:
	"""Main class for initialization and mechanics of the game"""
	def __init__(self, width=1200, height=720):
		pygame.init()
		pygame.display.set_caption('Xadir')
		self.width = width
		self.height = height
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.sidebar = pygame.Rect(960, 0, 240, 720)
		self.screen.fill((159, 182, 205))
		self.font = pygame.font.Font(None, 50)
		self.turntext = self.font.render('Player 0', True, (255,255, 255), (159, 182, 205))
		self.textRect = self.turntext.get_rect()
		self.textRect.centerx = self.sidebar.centerx
		self.textRect.centery = 50

	def main_loop(self):
		self.load_sprites()
		while 1:
			self.map_sprites.draw(self.screen)
			self.player_sprites.draw(self.screen)
			self.grid_sprites.draw(self.screen)
			self.screen.blit(self.turntext, self.textRect)
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					self.click()
				if event.type == KEYDOWN and event.key == K_SPACE:
					self.next_turn()
			pygame.display.flip()
			self.update_sprites()
			if self.players[self.turn].movement_points_left() < 1:
				self.next_turn()
			time.sleep(0.05)

	def load_sprites(self):
		"""Load the sprites that we need"""
		self.walkable = ['GGGG1']
		map, mapsize, spawns = load_map('map2.txt')
		self.map = background_map(map, *mapsize)
		self.spawns = spawns
		"""
		# player_1_spawn_points = random.sample(self.spawns[1], number_of_characters)
		self.players = []		
		# self.players.append(player([['b', 4, 3]], self))
		self.add_player([['b', 4, 3], ['b', 4, 6]])
		self.add_player([['b', 17, 10], ['b', 17, 13]])		
		"""
		self.players = []

		player_count = 2
		character_count = 2
		player_ids = random.sample(self.spawns, player_count)
		for player_id in player_ids:
			spawn_points = random.sample(self.spawns[player_id], character_count)
			self.add_player([('b', x, y) for x, y in spawn_points])

		self.turn = 0
		self.grid_sprites = pygame.sprite.Group()
		self.map_sprites = self.map.get_sprites()
		self.player_sprites = pygame.sprite.Group()
		for p in self.players:
			self.player_sprites.add(p.get_sprites())

	def click(self):
		player = self.players[self.turn]
		characters = player.get_characters()
		for i in range(len(characters)):
			char_coords = characters[i].get_coords()
			mouse_coords = list(pygame.mouse.get_pos())
			mouse_coords = [mouse_coords[0]/TILE_SIZE[0], mouse_coords[1]/TILE_SIZE[1]]
			#print char_coords
			#print mouse_coords
			if char_coords == mouse_coords:
				#print "You can move %d tiles" % (characters[i].get_movement_points())
				#print "Clicked on character"
				if characters[i].is_selected():
					characters[i].unselect()
					self.grid_sprites = pygame.sprite.Group()
				else:
					characters[i].select()
					if characters[i].get_movement_points() <= 0:
						self.movement_grid = sprite_grid([characters[i].get_coords()], characters[i].get_coords(), tiletypes['r'])
						self.grid_sprites = self.movement_grid.get_sprites()
					else:
						self.movement_grid = sprite_grid(characters[i].get_movement_grid(), characters[i].get_coords(), tiletypes['g'])
						self.grid_sprites = self.movement_grid.get_sprites()
			elif characters[i].is_selected():
				if characters[i].is_legal_move(mouse_coords):
					start = characters[i].get_coords()
					#print characters[i].is_attack_move(mouse_coords)
					"""					
					if characters[i].is_attack_move(mouse_coords):
						path = self.get_path(start, mouse_coords)
						print path						
						end = path[1]
						distance = max(abs(start[0] - end[0]), abs(start[1] - end[1]))
						#print "Moved %d tiles" % (distance)					
						characters[i].set_coords(end)					
						characters[i].reduce_movement_points(distance)
						self.grid_sprites = pygame.sprite.Group()
						characters[i].unselect
						for p in self.get_other_players():
							for c in p.get_characters():
								if c.get_coords() == mouse_coords:
									target = c
						self.attack(characters[i], target)
					"""
					if characters[i].is_attack_move(mouse_coords):
						print "false"
					else:
						end = mouse_coords
						distance = max(abs(start[0] - end[0]), abs(start[1] - end[1]))
						#print "Moved %d tiles" % (distance)					
						characters[i].set_coords(end)					
						characters[i].reduce_movement_points(distance)
						self.grid_sprites = pygame.sprite.Group()
						characters[i].unselect()
			if char_coords != mouse_coords:
				characters[i].unselect()

	def update_sprites(self):
		self.player_sprites = pygame.sprite.Group()
		for p in self.players:
			p.update_sprites()
			self.player_sprites.add(p.get_sprites())

	def next_turn(self):
		if len(self.players) < 1:
			print "Error, less than one player"
		elif len(self.players) == 1:
			print "There is only one player"
			self.turn = 0
		else:
			print "Next players turn"
			self.turn = (self.turn + 1) % (len(self.players))
			print self.turn
		self.players[self.turn].reset_movement_points()
		self.update_turntext()
	
	def update_turntext(self):
		turnstring = "Player " + str(self.turn)
		self.turntext = self.font.render(turnstring, True, (255,255, 255), (159, 182, 205))


	def get_all_players(self):
		return self.players

	def get_other_players(self):
		other_players = self.players
		other_players.pop(self.turn)
		return other_players

	def get_current_player(self):
		return self.players[self.turn]
	
	def get_own_other_players(self):
		return [self.players[self.turn], self.get_other_players()]

	def add_player(self, characters):
		self.players.append(player(characters, self))

	def get_path(self, start, end):
		path = []
		if start == end:
			return [start]
		else:
			temp = end
			path.append(temp)			
			while temp != start:
				if abs(temp[0] - start[0]) > abs(temp[1] - start[1]):
					temp[0] -= 1
					path.append(temp)
				elif abs(temp[0] - start[0]) < abs(temp[1] - start[1]):
					temp[1] -= 1
					path.append(temp)
				else:
					temp[0] -= 1
					temp[1] -= 1
					path.append(temp)
		path.append(start)
		return path
	
	def attack(attacker, target):
		print "Character at %d attacked character at %d" % (attacker.get_coords(), target.get_coords())

class sprite_grid:
	def __init__(self, grid, coords, tile):
		self.sprites = pygame.sprite.Group()
		for i in range(len(grid)):
			self.sprites.add(Tile(tile, pygame.Rect(grid[i][0]*TILE_SIZE[0], grid[i][1]*TILE_SIZE[1], *TILE_SIZE)))

	def get_sprites(self):
		return self.sprites

class background_map:
	"""Map class to create the background layer, holds any static and dynamical elements in the field."""
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

	def get_sprites(self):
		return self.sprites

	def get_map(self):
		return self.map

class player:
	"""Class to create player or team in the game. One player may have many characters."""
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
			coords.append(i.get_coords())
		return coords

	def select_character(self, character):
		self.characters[character].select()

	def unselect_character(self, character):
		self.characters[character].unselect()

	def character_is_selected(self, character):
		return self.characters[character].is_selected()

	def remove_character(self, i):
		characters.pop(i)

	def update_sprites(self):
		self.sprites = pygame.sprite.Group()
		for i in range(len(self.characters)):
			coords = self.characters[i].get_coords()
			character_type = self.characters[i].get_type()
			tile = tiletypes[character_type]
			self.sprites.add(Tile(tile, pygame.Rect(coords[0]*TILE_SIZE[0], coords[1]*TILE_SIZE[1], *TILE_SIZE)))

	def movement_points_left(self):
		points_left = 0
		for c in self.characters:
			points_left += c.get_movement_points()
		return points_left

	def reset_movement_points(self):
		for c in self.characters:
			c.set_movement_points(2)

class character:
	"""Universal class for any character in the game"""
	def __init__(self, character_type, movement, coords, heading, main):
		self.type = character_type		
		self.movement = movement	# Movement points left
		#self.health = health		# Health left
		self.coords = coords 		# Array of x and y
		self.heading = heading		# Angle from north in degrees, possible values are: 0, 45, 90, 135, 180, 225, 270 and 315
		self.selected = False
		self.main = main

		self.background_map = self.main.map.get_map()
		self.walkable_tiles = self.main.walkable
		self.players = self.main.get_all_players()

	def get_type(self):
		return self.type

	def set_type(self, character_type):
		self.type = character_type

	def get_coords(self):
		"""Returns coordinates of the character, return is array [x, y]"""
		return self.coords

	def set_coords(self, coords):
		"""Sets coordinates of characte, input is array of [x, y]"""
		self.coords = coords

	def get_heading(self):
		"""Returns heading of character in degrees"""
		return self.heading

	def set_heading(self, angle):
		"""Sets the absolute heading of character"""
		self.heading = angle

	def is_selected(self):
		return self.selected

	def select(self):
		self.selected = True

	def unselect(self):
		self.selected = False

	def get_movement_points(self):
		return self.movement

	def set_movement_points(self, points):
		self.movement = points

	def reduce_movement_points(self, points):
		self.movement = self.movement - points
		print "%d movement points left" % (self.movement)

	def turn(self, angle):
		"""Turns character given amount, relative to previous heading. For now only turns 90-degrees at a time"""
		angle = angle % 360
		if angle <= 45:
			self.heading = (self.heading + angle) % 360
		elif angle <= 90:
			self.heading = (self.heading + angle) % 360
		elif angle <= 135:
			self.heading = (self.heading + angle) % 360

	def move_forward(self, steps):
		"""Moves to headed direction given amount of steps"""
		if self.movement <= steps:
			if self.heading == 0:
				self.coords[1] -= steps
			elif self.heading == 90:
				self.coords[0] += steps
			elif self.heading == 180:
				self.coords[1] += steps
			elif self.heading == 270:
				self.coords[0] -= steps

	def get_movement_grid(self):
		"""Return grid of available cells to move to"""
		movement_grid = self.get_surroundings(self.coords)
		if self.movement > 1:
			for i in range(2, (self.movement + 1)):
				for i in range(len(movement_grid)):
					movement_grid.extend(self.get_surroundings(movement_grid[i]))
		movement_grid = [list(x) for x in set(tuple(x) for x in movement_grid)]
		return movement_grid

	def get_surroundings(self, coords):
		"""Return surrounding tiles that are walkable"""
		return_grid = []
		for x in range(-1, 2):
			for y in range(-1, 2):
				temp_coords = [coords[0] + x, coords[1] + y]
				#print temp_coords
				if self.is_walkable_tile(temp_coords): return_grid.append(temp_coords)
		return return_grid

	def is_walkable_tile(self, coords):
		"""To check if tile is walkable"""
		if coords[1] >= 15: return False
		if coords[0] >= 20: return False
		if coords[0] < 0: return False
		if coords[1] < 0: return False

		p = self.main.get_current_player()
		for c in p.get_characters_coords():
			if c == coords:
				return False

		for w in self.walkable_tiles:
			if self.background_map[coords[1]][coords[0]] == w:
				return True

		return False

	def is_legal_move(self, coords):
		"""Before moving, check if target is inside movement grid"""
		movement_grid = self.get_movement_grid()
		for i in range(len(movement_grid)):
			if coords == movement_grid[i]:
				return True
		return False

	def is_attack_move(self, coords):
		for p in self.main.get_other_players():
			for c in p.get_characters_coords():
				print c
				if c == coords:
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

if __name__ == "__main__":
	game = xadir_main()

	tiles = load_tiles('placeholder_tilemap.png', TILEGROUP_SIZE, (255, 0, 255), SCALE)
	characters = parse_tiles(tiles[1][2], TILE_SIZE)

	tiletypes = load_named_tiles('placeholder_tilemap', TILE_SIZE, (255, 0, 255), SCALE)
	tiletypes['b'] = characters[0][0]
	tiletypes['g'] = characters[1][0]
	tiletypes['r'] = characters[2][0]
	tiletypes['g'].set_alpha(120)
	tiletypes['r'].set_alpha(120)

	game.main_loop()
