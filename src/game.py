import os, sys, time
import pygame
import numpy
import math
import random
import Image
from pygame.locals import *
from resources import *
from grid import *
from algo import *
from UI import *

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

def sign(value):
	return cmp(value, 0)

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
	
# XXX: Adding some UI controls to game window
def write_button(self, surface, text, x, y):
		buttontext = self.buttonfont.render(text, True, (255,255, 255), (159, 182, 205))
		buttonrect = buttontext.get_rect()
		buttonrect.centerx = x
		buttonrect.centery = y
		surface.blit(buttontext, buttonrect)

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

def pygame_surface_from_pil_image(im):
	if im.mode not in ('RGB', 'RGBA'):
		im = im.convert('RGBA')
	data = im.tostring()
	return pygame.image.fromstring(data, im.size, im.mode)

def get_animation_frames(path):
	anim = Image.open(path)
	try:
		while 1:
			yield anim
			# This is ugly, but PIL seems to corrupt all the
			# other frames of animation as soon as you do
			# *anything* with one of them. You can't even
			# copy() each frame, you've just got to open the
			# image again for each frame and iterate to the
			# correct position. (Yeah, you can't even use
			# one seek to get there...)
			end = anim.tell()
			anim = Image.open(path)
			start = anim.tell()
			for pos in range(start, end + 1):
				anim.seek(pos+1)
	except EOFError:
		pass # end of sequence

class XadirMain:
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
		self.buttonfont = pygame.font.Font(FONT, int(50*FONTSCALE))
		self.buttons = []
		self.playerfont = pygame.font.Font(FONT, int(20*FONTSCALE))
		self.healthbars = []
		self.enemy_tiles = []
		self.clock = pygame.time.Clock()
		self.fps = 30
		self.showhealth = True
		self.buttons.append(Button(970, 600, 230, 100, "End turn", 40, self.screen, self.next_turn))

		self.sprites = pygame.sprite.LayeredDirty()

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
			pygame.display.flip()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						for b in self.buttons:
							if b.contains(*event.pos):
								f = b.get_function()
								f()
						self.click()
				if event.type == KEYDOWN and event.key == K_SPACE:
					self.next_turn()
			if self.players[self.turn].movement_points_left() < 1:
				self.next_turn()
			self.clock.tick(self.fps)
			self.hue += 10

	def draw(self):
		self.sprites.update()
		self.screen.fill((159, 182, 205))
		self.update_buttons()
		# XXX: less flashy way to indicate that we're running smoothly
		self.draw_fps(self.clock.get_fps(), get_hue_color(self.hue))
		self.map_sprites.draw(self.screen)
		self.grid_sprites.draw(self.screen)
		# Update layers
		self.sprites._spritelist.sort(key = lambda sprite: sprite._layer, reverse = True)
		self.sprites.draw(self.screen)
		for enemy_tiles in self.enemy_tiles:
			self.screen.blit(enemy_tiles[0], enemy_tiles[1])
		self.draw_turntext()
		self.draw_healthbars()

	def update_buttons(self):
		for b in self.buttons:
			b.draw()

	def draw_fps(self, fps, color):
		text = self.playerfont.render('fps: %d' % fps, True, color)
		rect = text.get_rect()
		rect.centerx = self.sidebar.centerx
		self.screen.blit(text, rect)

	def load_sprites(self):
		"""Load the sprites that we need"""
		self.walkable = [name for name in self.tiletypes.keys() if name.count('W') <= 1]
		map, mapsize, spawns = load_map(self.mapname)
		self.map = BackgroundMap(map, *mapsize, tiletypes = self.tiletypes)
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
		for p in self.players:
			self.sprites.add(p.all_characters)
			
	def click(self):
		mouse_pos = pygame.mouse.get_pos()
		mouse_grid_pos = (mouse_pos[0]/TILE_SIZE[0], mouse_pos[1]/TILE_SIZE[1])
		player = self.players[self.turn]
		for character in player.characters:
			if character.grid_pos == mouse_grid_pos:
				if character.is_selected():
					character.unselect()
					self.grid_sprites = pygame.sprite.Group()
				else:
					character.select()
					if character.mp <= 0:
						self.movement_grid = SpriteGrid([character.grid_pos], self.imgs['red'])
						self.grid_sprites = self.movement_grid.sprites
					else:
						self.movement_grid = SpriteGrid(self.get_action_area_for(character), self.imgs['green'])
						self.grid_sprites = self.movement_grid.sprites
			elif character.is_selected():
				self.grid_sprites = pygame.sprite.Group()
				character.unselect()
				if mouse_grid_pos in self.get_action_area_for(character):
					if character.is_attack_move(mouse_grid_pos):
						self.do_attack(character, mouse_grid_pos)
					else:
						self.do_move(character, mouse_grid_pos)
			if character.grid_pos != mouse_grid_pos:
				character.unselect()

	def do_attack(self, character, mouse_grid_pos):
		start = character.grid_pos
		path = self.get_attack_path_for(character, start, mouse_grid_pos)
		end = path[-2]
		distance = len(path) - 2
		self.animate_move(path, character)
		character.grid_pos = end
		character.mp -= distance
		character.set_heading(self.get_heading(end, mouse_grid_pos))
		target = None
		for p in self.get_other_players():
			for c in p.characters:
				if c.grid_pos == mouse_grid_pos:
					target = c
		self.attack(character, target)

	def do_move(self, character, mouse_grid_pos):
		start = character.grid_pos
		end = mouse_grid_pos
		path = self.get_move_path_for(character, start, end)
		distance = len(path) - 1
		self.animate_move(path, character)
		character.grid_pos = end
		character.mp -= distance
		new_heading = self.get_heading(path[-2], mouse_grid_pos)
		character.set_heading(new_heading)

	def animate_move(self, path, character):
		for i in range(1, len(path) - 1):
			character.set_heading(self.get_heading(path[i], path[i+1]))
			character.grid_pos = path[i]
			self.draw()
			pygame.display.flip()
			self.clock.tick(5)

	def animate_hit(self, coords, file_path):
		anim_rect = pygame.Rect(coords[0], coords[1] - 8*SCALE, 24, 32)

		for im in get_animation_frames(file_path):
			surface = pygame_surface_from_pil_image(im)
			surface = pygame.transform.scale(surface, (24*SCALE, 32*SCALE))
			self.draw()
			self.screen.blit(surface, anim_rect)
			pygame.display.flip()
			self.clock.tick(10)

	def animate_hp_change(self, character, change):
		change_sign = sign(change)
		change_amount = abs(change)
		orig_hp = character.hp
		for i in range(1, 30):
			character.hp = orig_hp + change_sign * scale(i, 30, change_amount)
			if character.hp < 1:
				break
			self.draw()
			pygame.display.flip()
			self.clock.tick(30)
		character.hp = orig_hp

	def get_heading(self, a, b):
		delta = (b[0] - a[0], b[1] - a[1])
		# Negate y because screen coordinates differ from math coordinates
		angle = math.degrees(math.atan2(-delta[1], delta[0])) % 360
		# Make the angle an integer and a multiple of 45
		angle = int(round(angle / 45)) * 45
		# Prefer horizontal directions when the direction is not a multiple of 90
		return {45: 0, 135: 180, 225: 180, 315: 0}.get(angle, angle)

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
			for character in player.all_characters:
				character_healthbar_rect = pygame.Rect(tuple(coords), tuple(bar_size))
				draw_main_hp_bar(self.screen, character_healthbar_rect, character.max_hp, character.hp)
				if self.showhealth:
					draw_char_hp_bar(self.screen, pygame.Rect((character.x + 2, character.y - (CHAR_SIZE[1] - TILE_SIZE[1])), (48-4, 8)), character.max_hp, character.hp)
				coords[1] += (bar_height + margin)

	def update_enemy_tiles(self):
		self.enemy_tiles = []
		players = self.get_other_players()
		for player in players:
			for character in player.characters:
				coords = character.grid_pos
				print "enemy alive at (%d,%d)" % (coords[0], coords[1])
				tile = self.character_mask(character.rect, character)
				self.enemy_tiles.append(tile)

	def get_all_players(self):
		return self.players

	def get_other_players(self):
		return [player for i, player in enumerate(self.players) if i != self.turn]

	def get_current_player(self):
		return self.players[self.turn]

	def get_own_other_players(self):
		return [self.players[self.turn], self.get_other_players()]

	def add_player(self, name, characters):
		self.players.append(Player(name, characters, self))

	def attack(self, attacker, target):
		attacker_position = attacker.grid_pos
		target_position = target.grid_pos
		print "Character at (%d,%d) attacked character at (%d,%d)" % (attacker_position[0], attacker_position[1], target_position[0], target_position[1])
		if attacker.mp > 0:
			self.animate_hit((target_position[0]*TILE_SIZE[0], target_position[1]*TILE_SIZE[1]), os.path.join(GFXDIR, "sword_hit_small.gif"))
			damage = roll_attack_damage(attacker, target)
			target.take_hit(damage * attacker.mp)
			attacker.mp = 0
		self.update_enemy_tiles()

	def is_walkable(self, coords):
		"""Is the terrain at this point walkable?"""
		grid = self.map.get_map()
		return coords in grid and grid[coords] in self.walkable

	def is_passable_for(self, character, coords):
		"""Is it okay for <character> to pass through this point without stopping?"""
		return self.is_walkable(coords) and coords not in [c.grid_pos for p in self.players for c in p.characters if p != character.player]

	def is_haltable_for(self, character, coords):
		"""Is it okay for <character> to stop at this point?"""
		return self.is_walkable(coords) and coords not in [c.grid_pos for p in self.players for c in p.characters if c != character]

	def get_move_path_for(self, character, start, end):
		"""Get path from start to end; all the intermediate points will be passable and the last one haltable"""
		assert isinstance(start, tuple)
		assert isinstance(end, tuple)
		assert self.is_haltable_for(character, end)
		return shortest_path(self, start, end, lambda self_, pos: self_.get_neighbours(pos, lambda pos_: self_.is_passable_for(character, pos_)))

	def get_attack_path_for(self, character, start, end):
		"""Get path suitable for attacking from start to end; ie. a path where you can stop on the point just *before* the last one"""
		assert isinstance(start, tuple)
		assert isinstance(end, tuple)
		assert end in [c.grid_pos for p in self.players for c in p.characters if p != character.player], 'Target square must contain enemy character'
		# Get possible stopping points, one square away from the enemy
		ends = self.get_neighbours(end, lambda pos: self.is_haltable_for(character, pos))
		path = shortest_path_any(self, start, set(ends), lambda self_, pos: self_.get_neighbours(pos, lambda pos_: self_.is_passable_for(character, pos_)))
		if path:
			path.append(end)
		return path

	def get_action_area_for(self, character):
		"""Get points where the character can either move or attack"""
		result = bfs_area(self, character.grid_pos, character.mp, lambda self_, pos: self_.get_neighbours(pos, lambda pos_: self_.is_walkable(pos_)) if self_.is_passable_for(character, pos) else [])
		# Remove own characters
		result = set(result) - set(c.grid_pos for c in character.player.characters)
		# Remove enemies that can't be reached
		result = result - set(c.grid_pos for p in self.players for c in p.characters if p != character.player and not self.get_neighbours(c.grid_pos, lambda pos: pos == character.grid_pos or pos in result))
		return list(result)

	def get_neighbours(self, coords, filter = None, size = 1):
		"""Get surrounding points, filtered by some function"""
		if filter is None:
			filter = lambda pos: True
		grid = self.map.get_map()
		result = [pos for pos in grid.env_keys(coords, size) if filter(pos)]
		result.sort(key = lambda pos: get_distance_2(pos, coords))
		return result

	def opaque_rect(self, rect, color=(0, 0, 0), opaque=255):
		box = pygame.Surface((rect.width, rect.height)).convert()
		box.fill(color)
		box.set_alpha(opaque)
		return [box, (rect.left, rect.top)]

	def character_mask(self, rect, character):
		tile = self.chartypes[character.type + '_' + str(character.get_heading())].convert_alpha()
		tile.fill((0, 0, 0, 200), special_flags=pygame.BLEND_RGBA_MULT)
		return (tile, (rect.left, rect.top))

class SpriteGrid:
	def __init__(self, grid, tile):
		self.sprites = pygame.sprite.Group()
		for i in range(len(grid)):
			self.sprites.add(Tile(tile, pygame.Rect(grid[i][0]*TILE_SIZE[0], grid[i][1]*TILE_SIZE[1], *TILE_SIZE)))

class BackgroundMap(Grid):
	"""Map class to create the background layer, holds any static and dynamical elements in the field."""
	def __init__(self, map, width, height, tiletypes):
		Grid.__init__(self, width, height, map)
		self.cell_size = TILE_SIZE
		self.x = self.y = 0
		self.map = self
		self.sprites = pygame.sprite.LayeredUpdates()
		for (x, y), tiletype in self.map.items():
			tile = tiletypes[tiletype]
			#print x, y
			self.sprites.add(Tile(tile, pygame.Rect(x*TILE_SIZE[0], y*TILE_SIZE[1], *TILE_SIZE), layer = y))

	def get_map(self):
		return self.map

class Player:
	"""Class to create player or team in the game. One player may have many characters."""
	def __init__(self, name, chardata, main):
		self.name = name
		self.main = main
		self.all_characters = [Character(self, type, 5, (x, y), heading, main) for type, x, y, heading in chardata]

	characters = property(lambda self: [character for character in self.all_characters if character.is_alive()])
	dead_characters = property(lambda self: [character for character in self.all_characters if not character.is_alive()])

	def get_characters_coords(self):
		coords = []
		for i in self.characters:
			coords.append(i.grid_pos)
		return coords

	def movement_points_left(self):
		points_left = 0
		for c in self.characters:
			points_left += c.mp
		return points_left

	def reset_movement_points(self):
		for c in self.all_characters:
			c.mp = c.max_mp

class Dice:
	def __init__(self, count, sides):
		self.count = count
		self.sides = sides

	def __repr__(self):
		return '%s(%d, %d)' % (self.__class__.__name__, self.count, self.sides)

	def __str__(self):
		return '%dd%d' % (self.count, self.sides)

	def roll(self):
		result = self.count + sum(random.randrange(self.sides) for i in range(self.count))
		print self, 'rolled', result
		return result

class Weapon:
	sizes = ['light', 'normal', 'heavy']
	types = ['melee', 'ranged', 'magic']
	damage_types = ['piercing', 'slashing', 'bludgeoning', 'magic'] # XXX Alexer: added magic
	classes = ['sword', 'dagger', 'spear', 'axe', 'bow', 'crossbow', 'wand']
	def __init__(self):
		self.size = random.choice(self.sizes)
		self.type = random.choice(self.types)
		self.class_ = random.choice(self.classes)
		self.damage = [(Dice(random.randrange(1, 4), random.randrange(4, 11, 2)), set([random.choice(self.damage_types)]))]
		self.magic_enchantment = random.randrange(11)

	def __repr__(self):
		return 'Weapon(%r, %r, %r, %r, %r)' % (self.size, self.type, self.class_, self.damage, self.magic_enchantment)

	def roll_damage(self):
		result = []
		for dice, damage_types in self.damage:
			damage = dice.roll()
			print self, 'rolled', damage, 'of', '/'.join(damage_types), 'damage'
			result.append((damage, damage_types))
		return result

class Armor:
	def __init__(self):
		self.miss_chance = random.randrange(-5, 6)
		self.damage_reduction = random.randrange(11)

def roll_attack_damage(attacker, defender):
	attacker_miss_chance = attacker.per_wc_miss_chance.get(attacker.weapon.class_, 10) - attacker.weapon.magic_enchantment * 2
	defender_evasion_chance = defender.terrain_miss_chance + defender.armor.miss_chance + math.floor(defender.dexterity / 5)
	miss_chance = attacker_miss_chance + defender_evasion_chance
	is_hit = random.randrange(100) < 100 - miss_chance
	print 'Miss chance:', miss_chance
	if not is_hit:
		print 'Missed!'
		return 0

	critical_chance = {'light': 15, 'normal': 10, 'heavy': 5}[attacker.weapon.size]
	critical_multiplier = {'light': 1.5, 'normal': 2.0, 'heavy': 3.0}[attacker.weapon.size]
	is_critical_hit = random.randrange(100) < critical_chance

	print 'Critical chance and multiplier:', critical_chance, critical_multiplier
	if is_critical_hit: print 'Critical!'
	damage_multiplier = critical_multiplier if is_critical_hit else 1

	wc_damage = {'melee': attacker.strength, 'ranged': attacker.dexterity, 'magic': attacker.intelligence}[attacker.weapon.type]
	#for weapon_damage, weapon_damage_types in attacker.weapon.roll_damage():
	weapon_damage = attacker.weapon.roll_damage()[0][0] # XXX Alexer: need to loop

	positive_damage = damage_multiplier * (weapon_damage + wc_damage + attacker.weapon.magic_enchantment)#+ attacker.class_(passive)_skill.damage # XXX Alexer: add passive skill damage
	negative_damage = defender.class_damage_reduction + math.floor(defender.constitution / 10) + defender.armor.damage_reduction
	damage = positive_damage - negative_damage # XXX Alexer: no total negative allowed

	print positive_damage, 'of damage and', negative_damage, 'of damage reduction: dealt', damage, 'of damage'

	return int(math.floor(damage))

class Character(UIGridObject, pygame.sprite.DirtySprite):
	"""Universal class for any character in the game"""
	def __init__(self, player, type, max_mp, coords, heading, main, max_hp = 100, attack_stat = 10):
		UIGridObject.__init__(self, main.map, coords)
		pygame.sprite.DirtySprite.__init__(self)

		self.player = player
		self.type = type
		# Movement points
		self.max_mp = max_mp
		self.mp = max_mp
		# Health points
		self.max_hp = max_hp
		self.hp = random.randrange(max_hp) # Randomized for testing look&feel
		# Stats
		self.dexterity = random.randrange(1, 20)
		self.constitution = random.randrange(1, 20)
		self.intelligence = random.randrange(1, 20)
		self.strength = random.randrange(1, 20)
		# Status
		self.heading = heading   # Angle from right to counter-clockwise in degrees, possible values are: 0, 45, 90, 135, 180, 225, 270 and 315
		self.selected = False
		self.alive = True

		self.terrain_miss_chance = 0 # XXX Alexer: lolfixthis :D
		self.per_wc_miss_chance = {}
		self.class_damage_reduction = random.randrange(11)
		self.armor = Armor()
		self.weapon = Weapon()

		self.main = main
		self.background_map = self.main.map.get_map()
		self.walkable_tiles = self.main.walkable
		self.players = self.main.get_all_players()

	def _get_rect(self): return pygame.Rect(self.x, self.y - (CHAR_SIZE[1] - TILE_SIZE[1]), *TILE_SIZE)
	rect = property(_get_rect)

	def update(self):
		self.image = self.main.chartypes[self.type + '_' + str(self.heading)]
		self.dirty = 1

	def get_heading(self):
		"""Returns heading of character in degrees"""
		return self.heading

	def set_heading(self, angle):
		"""Sets the absolute heading of character"""
		self.heading = angle

	def is_selected(self):
		return self.selected

	def take_hit(self, attack_points):
		print 'Took', attack_points, 'of damage'
		self.main.animate_hp_change(self, -attack_points)
		self.hp -= attack_points
		if self.hp < 1:
			self.hp = 0
			self.kill()

	def select(self):
		self.selected = True

	def unselect(self):
		self.selected = False

	def is_alive(self):
		return self.alive

	def revive(self):
		self.alive = True
		self.visible = True

	def kill(self):
		self.alive = False
		self.visible = False

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
				self.grid_y -= steps
			elif self.heading == 90:
				self.grid_x += steps
			elif self.heading == 180:
				self.grid_y += steps
			elif self.heading == 270:
				self.grid_x -= steps

	def is_attack_move(self, coords):
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


def start_game(mapname):
	game = XadirMain(mapname = mapname)
	game.load_resources()
	game.main_loop()

if __name__ == "__main__":
	start_game('map3.txt')
