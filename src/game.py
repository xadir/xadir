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

# XXX: Figure out how to do scaling better (output is new_max only if input is old_max)
def scale(value, old_max, new_max):
	assert value <= old_max
	return new_max * value / old_max

def get_hp_bar_color(total, value):
	"""Linearly generates colors from red to yellow to green"""
	# 256 values per color, so red-to-yellow and yellow-to-green make 512 - but yellow gets counted twice, so it's really 511
	num_colors = 511
	c = scale(value, total, num_colors)
	return (min(num_colors - c, 255), min(c, 255), 0)

# XXX: Possible optimization: Cache 100% health and do a partial blit instead of N+1 fills?
def draw_gradient_hp_bar(surface, rect, total, left):
	surface.fill((0, 0, 0), rect)
	for i in range(scale(left, total, rect.width)):
		color = get_hp_bar_color(rect.width - 1, i)
		surface.fill(color, (rect.x + i, rect.y, 1, rect.height))

def draw_solid_hp_bar(surface, rect, total, left):
	color = get_hp_bar_color(total, left)
	surface.fill(color, rect)

# Change to suit your mood
draw_hp_bar = draw_gradient_hp_bar

class xadir_main:
	"""Main class for initialization and mechanics of the game"""
	def __init__(self, width=1200, height=720):
		pygame.init()
		pygame.display.set_caption('Xadir')
		self.width = width
		self.height = height
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.sidebar = pygame.Rect(960, 0, 240, 720)
		self.font = pygame.font.Font(None, 50)
		self.healthbars = []
		self.enemy_tiles = []

	def main_loop(self):
		self.load_sprites()
		self.update_turntext()
		self.update_enemy_tiles()
		while 1:
			self.screen.fill((159, 182, 205))
			self.map_sprites.draw(self.screen)
			self.player_sprites.draw(self.screen)
			self.grid_sprites.draw(self.screen)
			self.screen.blit(self.turntext, self.textRect)
			self.update_healthbars()
			for healthbar in self.healthbars:
				self.screen.blit(healthbar[0], healthbar[1])
			for enemy_tiles in self.enemy_tiles:
				self.screen.blit(enemy_tiles[0], enemy_tiles[1])
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
		self.players = []

		player_count = 2
		character_count = 3
		player_ids = random.sample(self.spawns, player_count)
		player_names = random.sample('Alexer Zokol brenon Prototailz Ren'.split(), player_count)
		for player_id, name in zip(player_ids, player_names):
			spawn_points = random.sample(self.spawns[player_id], character_count)
			self.add_player(name, [('ball', x, y) for x, y in spawn_points])

		self.turn = 0
		self.grid_sprites = pygame.sprite.Group()
		self.map_sprites = self.map.get_sprites()
		self.masking_sprites = pygame.sprite.Group()
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
						self.movement_grid = sprite_grid([characters[i].get_coords()], characters[i].get_coords(), imgs['red'])
						self.grid_sprites = self.movement_grid.get_sprites()
					else:
						self.movement_grid = sprite_grid(characters[i].get_movement_grid(), characters[i].get_coords(), imgs['green'])
						self.grid_sprites = self.movement_grid.get_sprites()
			elif characters[i].is_selected():
				if characters[i].is_legal_move(mouse_coords):
					start = characters[i].get_coords()
					if characters[i].is_attack_move(mouse_coords):
						path = self.get_path(start, mouse_coords)
						print path
						end = path[(len(path) - 2)]
						distance = self.get_distance(start,end)
						#print "Moved %d tiles" % (distance)
						characters[i].set_coords(end)
						characters[i].reduce_movement_points(distance)
						self.grid_sprites = pygame.sprite.Group()
						characters[i].unselect
						target = 0
						for p in self.get_other_players():
							for c in p.get_characters():
								if c.get_coords() == mouse_coords:
									target = c
						if target == 0:
							print "Unable to fetch the character"
						self.attack(characters[i], target)
					else:
						end = mouse_coords
						distance = self.get_distance(start,end)
						#print "Moved %d tiles" % (distance)
						characters[i].set_coords(end)
						characters[i].reduce_movement_points(distance)
						self.grid_sprites = pygame.sprite.Group()
						characters[i].unselect()

					"""
					end = mouse_coords
					distance = max(abs(start[0] - end[0]), abs(start[1] - end[1]))
					#print "Moved %d tiles" % (distance)
					characters[i].set_coords(end)
					characters[i].reduce_movement_points(distance)
					self.grid_sprites = pygame.sprite.Group()
					characters[i].unselect()
					"""
			if char_coords != mouse_coords:
				characters[i].unselect()

	def update_sprites(self):
		self.player_sprites = pygame.sprite.Group()
		for p in self.players:
			p.update_sprites()
			self.player_sprites.add(p.get_sprites())
		"""
		self.masking_sprites = pygame.sprite.Group()
		tile = tiletypes['r']
		other_players = self.get_other_players()
		for p in other_players:
			coords = p.get_characters_coords()
			for c in coords:
				self.masking_sprites.add(Tile(tile, pygame.Rect(c[0]*TILE_SIZE[0], c[1]*TILE_SIZE[1], *TILE_SIZE)))
		"""

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
		self.update_enemy_tiles()
		self.update_turntext()

	def update_turntext(self):
		turnstring = self.players[self.turn].name
		self.turntext = self.font.render(turnstring, True, (255,255, 255), (159, 182, 205))
		self.textRect = self.turntext.get_rect()
		self.textRect.centerx = self.sidebar.centerx
		self.textRect.centery = 50

	def update_healthbars(self):
		coords = [(self.sidebar.left + 10), (self.sidebar.top + 100)]
		width = self.sidebar.width - 20
		height = self.sidebar.height - 110
		bar_height = 20
		margin = 5
		bar_size = [width, bar_height]
		self.healthbars = []
		players = self.get_all_players()
		for player in players:
			player_health = []
			characters = player.get_characters()
			text = player.name
			playerfont = pygame.font.Font(None, 20)
			playertext = playerfont.render(text, True, (255,255, 255), (159, 182, 205))
			playertextRect = playertext.get_rect()
			playertextRect.left = coords[0]
			playertextRect.top = coords[1]
			self.healthbars.append([playertext, playertextRect])
			coords[1] += 12 + margin
			for character in characters:
				character_healthbar_rect = pygame.Rect(tuple(coords), tuple(bar_size))
				draw_hp_bar(self.screen, character_healthbar_rect, character.get_max_health(), character.get_health())
				coords[1] += (bar_height + margin)

	def update_character_numbers(self):
		players = self.get_all_players()
		for p, player in enumerate(players):
			for character in player.get_characters():
				coords = character.get_coords()
				print "%s at (%d,%d)" % (player.name, coords[0], coords[1])
				self.add_text(self.screen, str(p), 20, (0, 0))

	def update_enemy_tiles(self):
		self.enemy_tiles = []
		players = self.get_other_players()
		for player in players:
			for character in player.get_characters():
				coords = character.get_coords()
				print "enemy at (%d,%d)" % (coords[0], coords[1])
				tile = self.opaque_rect(pygame.Rect(coords[0]*TARGET_SIZE, coords[1]*TARGET_SIZE, 48, 48), (0, 0, 0), 50)
				self.enemy_tiles.append(tile)

	def get_all_players(self):
		return self.players

	def get_other_players(self):
		if self.turn == 0:
			other_players = self.players[1:]
		elif self.turn == (len(self.players) - 1):
			other_players = self.players[:(len(self.players) - 1)]
		else:
			other_players = []
			other_players.append(self.players[0:(self.turn - 1)])
			other_players.append(self.players[(self.turn + 1):(len(self.players) - 1)])
		return other_players

	def get_current_player(self):
		return self.players[self.turn]

	def get_own_other_players(self):
		return [self.players[self.turn], self.get_other_players()]

	def add_player(self, name, characters):
		self.players.append(player(name, characters, self))

	def get_path(self, start, end):
		path = []
		if start == end:
			return [start, end]
		else:
			temp = start
			path.append(temp)
			while temp != end:
				print path
				for c in self.get_surroundings(temp):
					if self.get_distance(temp, end) > self.get_distance(c, end): temp = c
				path.append(temp)
				"""
				if temp[0] > start[0] and :
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
				"""
		return path

	def attack(self, attacker, target):
		attacker_position = attacker.get_coords()
		target_position = target.get_coords()
		print "Character at (%d,%d) attacked character at (%d,%d)" % (attacker_position[0], attacker_position[1], target_position[0], target_position[1])
		target.take_hit(attacker.attack)

	def get_surroundings(self, coords):
		"""Return surrounding tiles that are walkable"""
		return_grid = []
		for x in range(-1, 2):
			for y in range(-1, 2):
				temp_coords = [coords[0] + x, coords[1] + y]
				if self.is_walkable_tile(temp_coords): return_grid.append(temp_coords)
		return return_grid

	def is_walkable_tile(self, coords):
		"""To check if tile is walkable"""
		if coords[1] >= 15: return False
		if coords[0] >= 20: return False
		if coords[0] < 0: return False
		if coords[1] < 0: return False

		p = self.get_current_player()
		for c in p.get_characters_coords():
			if c == coords:
				return False

		background_map = self.map.get_map()
		for w in self.walkable:
			if background_map[coords[1]][coords[0]] == w:
				return True

		return False

	def get_distance(self, a, b):
		return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

	def add_text(self, surface, text, size, coords):
		textfont = pygame.font.Font(None, size)
		text_surface = textfont.render(text, True, (255,255, 255), (159, 182, 205))
		text_rect = text_surface.get_rect()
		text_rect.centerx = coords[0]
		text_rect.centery = coords[1]
		self.screen.blit(text_surface, text_rect)

	def opaque_rect(self, rect, color=(0, 0, 0), opaque=255):
		box = pygame.Surface((rect.width, rect.height)).convert()
		box.fill(color)
		box.set_alpha(opaque)
		return [box, (rect.left, rect.top)]

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
	def __init__(self, name, coords, main):
		self.name = name
		self.main = main
		self.coords = coords
		self.sprites = pygame.sprite.Group()
		self.characters = []
		for i in range(len(coords)):
			character_type = coords[i][0]
			y = coords[i][1]
			x = coords[i][2]
			tile = chartypes[character_type]
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
			if self.characters[i].is_alive():
				coords = self.characters[i].get_coords()
				character_type = self.characters[i].get_type()
				tile = chartypes[character_type]
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
	def __init__(self, character_type, movement, coords, heading, main, health = 100, attack = 10):
		self.type = character_type
		self.movement = movement # Movement points left
		self.max_health = health
		self.health = random.randrange(health) # Health left (0-100)
		self.attack = attack     # Attack points (0-50)
		self.coords = coords     # Array of x and y
		self.heading = heading   # Angle from north in degrees, possible values are: 0, 45, 90, 135, 180, 225, 270 and 315
		self.selected = False
		self.alive = True
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

	def get_max_health(self):
		return self.max_health

	def get_health(self):
		return self.health

	def set_health(self, health):
		self.health = health

	def take_hit(self, attack_points):
		self.health -= attack_points
		if self.health < 1:
			self.kill()

	def get_attack(self):
		return self.attack

	def set_attack(self):
		self.attack = attack

	def select(self):
		self.selected = True

	def unselect(self):
		self.selected = False

	def is_alive(self):
		return self.alive

	def revive(self):
		self.alive = True

	def kill(self):
		self.alive = False

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

	chartypes = {}
	chartypes['ball'] = characters[0][0]

	imgs = {}
	imgs['green'] = characters[1][0]
	imgs['red'] = characters[2][0]
	imgs['green'].set_alpha(120)
	imgs['red'].set_alpha(120)

	game.main_loop()

