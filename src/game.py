import os, sys, time
import pygame
import numpy
import math
import random
import Image
from pygame.locals import *
from resources import *
from algo import *

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

def get_distance_2(pos1, pos2):
	"""Get squared euclidean distance"""
	return (pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2

def div_ceil(dividend, divisor):
	"""Integer division, but with result rounded up instead"""
	return (dividend - 1) / divisor + 1

# XXX: Figure out how to do scaling better (output is new_max only if input is old_max)
def scale_floor(value, old_max, new_max):
	"""Scaling function where the result is new_max only when the input is old_max"""
	assert value >= 0
	assert value <= old_max
	return new_max * value / old_max

def scale_ceil(value, old_max, new_max):
	"""Scaling function where the result is 0 only when the input is 0"""
	assert value >= 0
	assert value <= old_max
	return div_ceil(new_max * value, old_max)

scale = scale_ceil

def get_hp_bar_color(total, value):
	"""Linearly generates colors from red to yellow to green"""
	# 256 values per color, so red-to-yellow and yellow-to-green make 512 - but yellow gets counted twice, so it's really 511
	num_colors = 511
	c = scale(value, total, num_colors)
	return (min(num_colors - c, 255), min(c, 255), 0)

# XXX: Possible optimization: Cache 100% health and do a partial blit instead of N+1 fills?
def draw_gradient_hp_bar(surface, rect, total, left):
	surface.fill((0, 0, 0), rect)
	for i in range(scale_ceil(left, total, rect.width)):
		color = get_hp_bar_color(rect.width - 1, i)
		surface.fill(color, (rect.x + i, rect.y, 1, rect.height))

def draw_solid_hp_bar(surface, rect, total, left):
	color = get_hp_bar_color(total, left)
	surface.fill(color, rect)

def draw_solid_hp_bar2(surface, rect, total, left):
	color = get_hp_bar_color(total, left)
	surface.fill((0, 0, 0), rect)
	surface.fill(color, (rect.x, rect.y, scale_ceil(left, total, rect.width), rect.height))

def get_hue_color(i):
	# red-yellow-green-cyan-blue-magenta-red
	# 6*256-6 = 1530

	#0 = red
	#255 = yellow
	#510 = green
	#765 = cyan
	#1020 = blue
	#1275 = magenta
	#1530 = red

	n = lambda c: max(min(c, 255), 0)

	r = n(abs(765-((i+0)%1530))-255)
	g = n(abs(765-((i+510)%1530))-255)
	b = n(abs(765-((i+1020)%1530))-255)

	return (r, g, b)

# Change to suit your mood
draw_main_hp_bar = draw_gradient_hp_bar
draw_char_hp_bar = draw_solid_hp_bar2

class xadir_main:
	"""Main class for initialization and mechanics of the game"""
	def __init__(self, width=1200, height=720, mapname='map2.txt'):
		pygame.init()
		pygame.display.set_caption('Xadir')
		self.mapname = mapname
		self.width = width
		self.height = height
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.sidebar = pygame.Rect(960, 0, 240, 720)
		self.font = pygame.font.Font(FONT, int(50*FONTSCALE))
		self.playerfont = pygame.font.Font(FONT, int(20*FONTSCALE))
		self.healthbars = []
		self.enemy_tiles = []
		self.clock = pygame.time.Clock()
		self.fps = 30
		self.showhealth = True

	def load_resources(self):
		tiles = load_tiles('placeholder_other24.png', TILE_SIZE, (255, 0, 255), SCALE)
		chars1 = load_tiles('sprite_collection.png', CHAR_SIZE, (255, 0, 255), SCALE)
		chars2 = load_tiles('sprite_collection_2.png', CHAR_SIZE, (255, 0, 255), SCALE)

		self.tiletypes = load_named_tiles('placeholder_tilemap24', TILE_SIZE, (255, 0, 255), SCALE)

		self.charnames = []
		self.chartypes = {}
		for i, char in enumerate(chars1[:-1] + chars2):
			name = 'char' + str(i+1)
			self.charnames.append(name)
			self.chartypes[name + '_270'] = char[0]
			self.chartypes[name + '_180'] = char[1]
			self.chartypes[name + '_0'] = char[2]
			self.chartypes[name + '_90'] = char[3]

		self.imgs = {}
		self.imgs['green'] = tiles[1][0]
		self.imgs['red'] = tiles[2][0]
		self.imgs['green'].set_alpha(120)
		self.imgs['red'].set_alpha(120)

	def main_loop(self):
		self.load_sprites()
		self.update_enemy_tiles()

		self.hue = 0
		while 1:
			self.draw()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					self.click()
				if event.type == KEYDOWN and event.key == K_SPACE:
					self.next_turn()
			if self.players[self.turn].movement_points_left() < 1:
				self.next_turn()
			self.clock.tick(self.fps)
			self.hue += 10

	def draw(self):
		self.update_sprites()
		self.screen.fill((159, 182, 205))
		# XXX: less flashy way to indicate that we're running smoothly
		self.draw_fps(self.clock.get_fps(), get_hue_color(self.hue))
		self.map_sprites.draw(self.screen)
		self.player_sprites.draw(self.screen)
		self.grid_sprites.draw(self.screen)
		self.draw_turntext()
		self.draw_healthbars()
		for enemy_tiles in self.enemy_tiles:
			self.screen.blit(enemy_tiles[0], enemy_tiles[1])
		pygame.display.flip()

	def draw_fps(self, fps, color):
		text = self.playerfont.render('fps: %d' % fps, True, color)
		rect = text.get_rect()
		rect.centerx = self.sidebar.centerx
		self.screen.blit(text, rect)

	def load_sprites(self):
		"""Load the sprites that we need"""
		self.walkable = [name for name in self.tiletypes.keys() if name.count('W') <= 1]
		map, mapsize, spawns = load_map(self.mapname)
		self.map = background_map(map, *mapsize, tiletypes = self.tiletypes)
		self.spawns = spawns
		self.players = []

		player_count = 2
		character_count = 3
		player_ids = random.sample(self.spawns, player_count)
		player_names = random.sample('Alexer Zokol brenon Prototailz Ren'.split(), player_count)
		for player_id, name in zip(player_ids, player_names):
			spawn_points = random.sample(self.spawns[player_id], character_count)
			self.add_player(name, [(random.choice(self.charnames), x, y, 0) for x, y in spawn_points])

		self.turn = 0
		self.grid_sprites = pygame.sprite.Group()
		self.map_sprites = self.map.sprites
		self.masking_sprites = pygame.sprite.Group()
		self.player_sprites = pygame.sprite.LayeredUpdates()
		for p in self.players:
			self.player_sprites.add(p.sprites)

	def click(self):
		mouse_coords = pygame.mouse.get_pos()
		mouse_coords = (mouse_coords[0]/TILE_SIZE[0], mouse_coords[1]/TILE_SIZE[1])
		player = self.players[self.turn]
		characters = player.characters
		for i in range(len(characters)):
			char_coords = characters[i].get_coords()
			if char_coords == mouse_coords:
				if characters[i].is_selected():
					characters[i].unselect()
					self.grid_sprites = pygame.sprite.Group()
				else:
					characters[i].select()
					if characters[i].mp <= 0:
						self.movement_grid = sprite_grid([characters[i].get_coords()], characters[i].get_coords(), self.imgs['red'])
						self.grid_sprites = self.movement_grid.sprites
					else:
						self.movement_grid = sprite_grid(characters[i].get_movement_grid(), characters[i].get_coords(), self.imgs['green'])
						self.grid_sprites = self.movement_grid.sprites
			elif characters[i].is_selected():
				if characters[i].is_legal_move(mouse_coords):
					start = characters[i].get_coords()
					if characters[i].is_attack_move(mouse_coords):
						path = self.get_path(start, mouse_coords)
						end = path[len(path) - 2]
						distance = len(path) - 2
						self.move_character(path, characters[i])
						characters[i].set_coords(end)
						characters[i].mp -= distance
						characters[i].set_heading(self.get_heading(end, mouse_coords))
						self.grid_sprites = pygame.sprite.Group()
						characters[i].unselect()
						target = None
						for p in self.get_other_players():
							for c in p.characters:
								if c.get_coords() == mouse_coords:
									target = c
						self.attack(characters[i], target)
					else:
						end = mouse_coords
						path = self.get_path(start, end)
						distance = len(path) - 1
						self.move_character(path, characters[i])
						characters[i].set_coords(end)
						characters[i].mp -= distance
						new_heading = self.get_heading(path[(len(path)-2)], mouse_coords)
						characters[i].set_heading(new_heading)
						self.grid_sprites = pygame.sprite.Group()
						characters[i].unselect()
				else:
					characters[i].unselect()
					self.grid_sprites = pygame.sprite.Group()
			if char_coords != mouse_coords:
				characters[i].unselect()

	def move_character(self, path, character):
		for i in range(1, len(path) - 1):
			character.set_heading(self.get_heading(path[i], path[i+1]))
			character.set_coords(path[i])
			self.draw()
			self.clock.tick(3)

	def animation(self, coords, file_path):
		anim = Image.open(file_path).convert("RGBA")
		anim_rect = pygame.Rect(coords[0], coords[1], 24, 32)
		try:
			while 1:
				anim.seek(anim.tell()+1)
				mode = anim.mode
				size = anim.size
				data = anim.tostring()

				assert mode in "RGB", "RGBA"

				surface = pygame.image.fromstring(data, size, mode)
				self.screen.blit(surface, anim_rect)
				self.clock.tick(3)
		except EOFError:
			pass # end of sequence

	def get_heading(self, a, b):
		print a
		print b
		delta_coords = (b[0] - a[0], b[1] - a[1])
		print delta_coords
		if delta_coords == (1, 0):
			return 0
		elif delta_coords == (1, 1):
			#return 45
			return 0
		elif delta_coords == (0, 1):
			return 270
		elif delta_coords == (-1, 1):
			#return 135
			return 180
		elif delta_coords == (-1, 0):
			return 180
		elif delta_coords == (-1, -1):
			#return 225
			return 180
		elif delta_coords == (0, -1):
			return 90
		elif delta_coords == (1, -1):
			#return 315
			return 0
		else:
			return 0

	def update_sprites(self):
		self.player_sprites = pygame.sprite.LayeredUpdates()
		for p in self.players:
			p.update_sprites()
			self.player_sprites.add(p.sprites)

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

	def draw_turntext(self):
		turnstring = self.players[self.turn].name
		turntext = self.font.render(turnstring, True, (255,255, 255), (159, 182, 205))
		rect = turntext.get_rect()
		rect.centerx = self.sidebar.centerx
		rect.centery = 50
		self.screen.blit(turntext, rect)

	def draw_healthbars(self):
		coords = [(self.sidebar.left + 10), (self.sidebar.top + 100)]
		width = self.sidebar.width - 20
		height = self.sidebar.height - 110
		bar_height = 20
		margin = 5
		bar_size = [width, bar_height]
		players = self.get_all_players()
		for player in players:
			text = player.name
			playertext = self.playerfont.render(text, True, (255,255, 255), (159, 182, 205))
			rect = playertext.get_rect()
			rect.left = coords[0]
			rect.top = coords[1]
			self.screen.blit(playertext, rect)
			# XXX: take this from text rect size?
			coords[1] += 12 + margin
			for character in player.characters:
				character_healthbar_rect = pygame.Rect(tuple(coords), tuple(bar_size))
				draw_main_hp_bar(self.screen, character_healthbar_rect, character.max_hp, character.hp)
				if self.showhealth:
					draw_char_hp_bar(self.screen, pygame.Rect((character.coords[0] * TILE_SIZE[0]+2, character.coords[1] * TILE_SIZE[1] - (CHAR_SIZE[1]-TILE_SIZE[1])), (48-4, 8)), character.max_hp, character.hp)
				coords[1] += (bar_height + margin)

	def update_character_numbers(self):
		players = self.get_all_players()
		for p, player in enumerate(players):
			for character in player.characters:
				coords = character.get_coords()
				print "%s at (%d,%d)" % (player.name, coords[0], coords[1])
				self.add_text(self.screen, str(p), 20, (0, 0))

	def update_enemy_tiles(self):
		self.enemy_tiles = []
		players = self.get_other_players()
		for player in players:
			for character in player.characters:
				if character.is_alive():
					coords = character.get_coords()
					print "enemy alive at (%d,%d)" % (coords[0], coords[1])
					tile = self.opaque_rect(pygame.Rect(coords[0]*TILE_SIZE[0], coords[1]*TILE_SIZE[1]-(CHAR_SIZE[1]-TILE_SIZE[1]), *CHAR_SIZE), (0, 0, 0), 50)
					self.enemy_tiles.append(tile)
				else:
					coords = character.get_coords()
					print "enemy dead at (%d,%d)" % (coords[0], coords[1])

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
		"""
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
		path = shortest_path(self, tuple(start), tuple(end), xadir_main.get_surroundings)
		return path

	def attack(self, attacker, target):
		attacker_position = attacker.get_coords()
		target_position = target.get_coords()
		print "Character at (%d,%d) attacked character at (%d,%d)" % (attacker_position[0], attacker_position[1], target_position[0], target_position[1])
		if attacker.mp > 0:
			target.take_hit((attacker.attack_stat * attacker.mp))
			self.animation((target_position[0]*TILE_SIZE[0], target_position[1]*TILE_SIZE[1]), os.path.join(GFXDIR, "sword_hit_small.gif"))
			attacker.mp = 0
		self.update_enemy_tiles()

	def get_surroundings(self, coords):
		"""Return surrounding tiles that are walkable"""
		assert isinstance(coords, tuple)
		return_grid = []
		for x in range(-1, 2):
			for y in range(-1, 2):
				temp_coords = (coords[0] + x, coords[1] + y)
				if self.is_walkable_tile(temp_coords): return_grid.append(temp_coords)
		return_grid.sort(key = lambda pos2: get_distance_2(pos2, coords))
		return return_grid

	def is_walkable_tile(self, coords):
		"""To check if tile is walkable"""
		assert isinstance(coords, tuple)
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

	def add_text(self, surface, text, size, coords):
		assert isinstance(coords, tuple)
		textfont = pygame.font.Font(FONT, int(size*FONTSCALE))
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

class background_map:
	"""Map class to create the background layer, holds any static and dynamical elements in the field."""
	def __init__(self, map, width, height, tiletypes):
		self.width = width
		self.height = height
		self.map = map
		self.sprites = pygame.sprite.LayeredUpdates()
		for y in range(self.height):
			for x in range(self.width):
				tiletype = self.map[y][x]
				tile = tiletypes[tiletype]
				#print x, y
				self.sprites.add(Tile(tile, pygame.Rect(x*TILE_SIZE[0], y*TILE_SIZE[1], *TILE_SIZE), layer = y))

	def get_map(self):
		return self.map

class player:
	"""Class to create player or team in the game. One player may have many characters."""
	def __init__(self, name, coords, main):
		self.name = name
		self.main = main
		self.coords = coords
		self.sprites = pygame.sprite.LayeredUpdates()
		self.characters = []
		for i in range(len(coords)):
			character_type = coords[i][0]
			x = coords[i][1]
			y = coords[i][2]
			heading = coords[i][3]
			tile = main.chartypes[character_type + '_' + str(heading)]
			self.sprites.add(Tile(tile, pygame.Rect(x*TILE_SIZE[0], y*TILE_SIZE[1], *TILE_SIZE), layer = y))
			self.characters.append(character(character_type, 5, (x, y), heading, self.main))

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

	def update_sprites(self):
		self.sprites = pygame.sprite.LayeredUpdates()
		for i in range(len(self.characters)):
			if self.characters[i].is_alive():
				coords = self.characters[i].get_coords()
				heading = self.characters[i].get_heading()
				character_type = self.characters[i].type
				tile = self.main.chartypes[character_type + '_' + str(heading)]
				self.sprites.add(Tile(tile, pygame.Rect(coords[0]*TILE_SIZE[0], coords[1]*TILE_SIZE[1]-(CHAR_SIZE[1]-TILE_SIZE[1]), *TILE_SIZE), layer = coords[1]))

	def movement_points_left(self):
		points_left = 0
		for c in self.characters:
			if c.is_alive():
				points_left += c.mp
		return points_left

	def reset_movement_points(self):
		for c in self.characters:
			c.mp = c.max_mp

class character:
	"""Universal class for any character in the game"""
	def __init__(self, type, max_mp, coords, heading, main, max_hp = 100, attack_stat = 10):
		self.type = type
		# Movement points
		self.max_mp = max_mp
		self.mp = max_mp
		# Health points
		self.max_hp = max_hp
		self.hp = random.randrange(max_hp) # Randomized for testing look&feel
		# Stats
		self.attack_stat = attack_stat     # Attack multiplier
		# Status
		assert isinstance(coords, tuple)
		self.coords = coords     # Tuple of x and y
		self.heading = heading   # Angle from right to counter-clockwise in degrees, possible values are: 0, 45, 90, 135, 180, 225, 270 and 315
		self.selected = False
		self.alive = True

		self.main = main
		self.background_map = self.main.map.get_map()
		self.walkable_tiles = self.main.walkable
		self.players = self.main.get_all_players()

	def get_coords(self):
		"""Returns coordinates of the character, return is tuple (x, y)"""
		assert isinstance(self.coords, tuple)
		return self.coords

	def set_coords(self, coords):
		"""Sets coordinates of characte, input is tuple of (x, y)"""
		assert isinstance(coords, tuple)
		self.coords = coords

	def get_heading(self):
		"""Returns heading of character in degrees"""
		return self.heading

	def set_heading(self, angle):
		"""Sets the absolute heading of character"""
		self.heading = angle

	def is_selected(self):
		return self.selected

	def take_hit(self, attack_points):
		self.hp -= attack_points
		if self.hp < 1:
			self.kill()

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
		return list(bfs_area(self, tuple(self.coords), self.mp, character.get_surroundings))

	def get_surroundings(self, coords):
		"""Return surrounding tiles that are walkable"""
		assert isinstance(coords, tuple)
		return_grid = []
		for x in range(-1, 2):
			for y in range(-1, 2):
				temp_coords = (coords[0] + x, coords[1] + y)
				#print temp_coords
				if self.is_walkable_tile(temp_coords): return_grid.append(temp_coords)
		return return_grid

	def is_walkable_tile(self, coords):
		"""To check if tile is walkable"""
		assert isinstance(coords, tuple)
		if coords[1] >= 15: return False
		if coords[0] >= 20: return False
		if coords[0] < 0: return False
		if coords[1] < 0: return False

		p = self.main.get_current_player()
		for c in p.characters:
			if c.get_coords() == coords:
				if c.is_alive():
					return False

		for w in self.walkable_tiles:
			if self.background_map[coords[1]][coords[0]] == w:
				return True

		return False

	def is_legal_move(self, coords):
		"""Before moving, check if target is inside movement grid"""
		assert isinstance(coords, tuple)
		movement_grid = self.get_movement_grid()
		for i in range(len(movement_grid)):
			if coords == movement_grid[i]:
				return True
		return False

	def is_attack_move(self, coords):
		assert isinstance(coords, tuple)
		for p in self.main.get_other_players():
			for c in p.get_characters_coords():
				if c == coords:
					return True
		return False

# Following classes define the graphical elements, or Sprites.

class Tile(pygame.sprite.Sprite):
	def __init__(self, image, rect=None, layer=0):
		pygame.sprite.Sprite.__init__(self)
		self.image = image
		self.rect = image.get_rect()
		self._layer = layer
		if rect is not None:
			self.rect = rect

def start_game(mapname):
	game = xadir_main(mapname = mapname)
	game.load_resources()
	game.main_loop()

if __name__ == "__main__":
	start_game('map3.txt')
