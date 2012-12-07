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

from dice import Dice
from races import races, Race
from armors import armors, Armor
from weapons import weapons, Weapon

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

L_MAP = 0
L_SEL = 1
L_CHAR = 2

L_CHAR_OVERLAY = 0
L_CHAR_EFFECT = 1

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

def get_animation_surfaces(path):
	for im in get_animation_frames(path):
		surface = pygame_surface_from_pil_image(im)
		rect = surface.get_rect()
		yield pygame.transform.scale(surface, (rect.width * SCALE, rect.height * SCALE))

class XadirMain:
	"""Main class for initialization and mechanics of the game"""
	def __init__(self, width=1200, height=720, mapname='map2.txt'):
		pygame.init()
		pygame.display.set_caption('Xadir')
		self.mapname = mapname
		self.width = width
		self.height = height
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.background = pygame.Surface((self.width, self.height))
		self.background.fill((159, 182, 205))
		self.sidebar = pygame.Rect(960, 0, 240, 720)
		self.font = pygame.font.Font(FONT, int(50*FONTSCALE))
		self.buttonfont = pygame.font.Font(FONT, int(50*FONTSCALE))
		self.buttons = []
		self.playerfont = pygame.font.Font(FONT, int(20*FONTSCALE))
		self.healthbars = []
		self.enemy_tiles = []
		self.clock = pygame.time.Clock()
		self.fps = 30
		self.showhealth = False
		self.buttons.append(Button(970, 600, 230, 100, "End turn", 40, self.screen, self.next_turn))

		self.disabled_chartypes = {}

		self.sprites = pygame.sprite.LayeredDirty(_time_threshold = 1000.0)
		self.sprites.add(Fps(self.clock, self.sidebar.centerx))
		self.sprites.add(CurrentPlayerName(self, self.sidebar.centerx))

	current_player = property(lambda self: self.players[self.turn])

	def load_resources(self):
		tiles = load_tiles('placeholder_other24.png', TILE_SIZE, (255, 0, 255), SCALE)
		raceimages = load_tiles('races.png', CHAR_SIZE, (255, 0, 255), SCALE)
		racenames = file(os.path.join(GFXDIR, 'races.txt')).read().split('\n')

		self.tiletypes = load_named_tiles('placeholder_tilemap24', TILE_SIZE, (255, 0, 255), SCALE)

		self.chartypes = {}
		for name, char in zip(racenames, raceimages):
			self.chartypes[name] = {270: char[0], 180: char[1], 0: char[2], 90: char[3]}

		self.imgs = {}
		self.imgs['green'] = tiles[1][0]
		self.imgs['red'] = tiles[2][0]
		self.imgs['green'].set_alpha(120)
		self.imgs['red'].set_alpha(120)

	def main_loop(self):
		self.load_sprites()
		self.init_sidebar()

		while 1:
			self.draw()
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

	def draw(self):
		self.clock.tick(self.fps)
		self.sprites.update()
		self.sprites.clear(self.screen, self.background)
		self.update_buttons()
		# Update layers
		self.sprites._spritelist.sort(key = lambda sprite: sprite._layer)
		self.sprites.draw(self.screen)
		pygame.display.flip()

	def update_buttons(self):
		for b in self.buttons:
			b.draw()

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
			self.add_player(name, [(random.choice(self.chartypes.keys()), x, y, 0) for x, y in spawn_points])

		self.turn = 0
		self.grid_sprites = pygame.sprite.Group()
		self.map_sprites = self.map.sprites
		self.sprites.add(self.map_sprites)
		for p in self.players:
			self.sprites.add(p.all_characters)
			for c in p.all_characters:
				self.sprites.add(DisabledCharacter(self, c))

	def set_grid_sprites(self, sprites):
		self.sprites.remove(self.grid_sprites)
		self.grid_sprites = sprites
		self.sprites.add(self.grid_sprites)

	def click(self):
		mouse_pos = pygame.mouse.get_pos()
		mouse_grid_pos = (mouse_pos[0]/TILE_SIZE[0], mouse_pos[1]/TILE_SIZE[1])
		player = self.players[self.turn]
		for character in player.characters:
			if character.grid_pos == mouse_grid_pos:
				if character.is_selected():
					character.unselect()
					self.set_grid_sprites(pygame.sprite.Group())
				else:
					character.select()
					if character.mp <= 0:
						self.movement_grid = SpriteGrid([character.grid_pos], self.imgs['red'])
						self.set_grid_sprites(self.movement_grid.sprites)
					else:
						self.movement_grid = SpriteGrid(self.get_action_area_for(character), self.imgs['green'])
						self.set_grid_sprites(self.movement_grid.sprites)
			elif character.is_selected():
				self.set_grid_sprites(pygame.sprite.Group())
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
		character.heading = self.get_heading(end, mouse_grid_pos)
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
		character.heading = new_heading

	def animate_move(self, path, character):
		for i in range(1, len(path) - 1):
			character.heading = self.get_heading(path[i], path[i+1])
			character.grid_pos = path[i]
			for i in range(6):
				self.draw()

	def animate_hit(self, character, file_path):
		anim = Animation(character, file_path, 3)

		self.sprites.add(anim)

		while anim.visible:
			self.draw()

		self.sprites.remove(anim)

	def animate_hp_change(self, character, change):
		change_sign = sign(change)
		change_amount = abs(change)
		orig_hp = character.hp
		for i in range(1, 30):
			character.hp = orig_hp + change_sign * scale(i, 30, change_amount)
			if character.hp < 1:
				break
			self.draw()
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
			self.animate_hit(target, os.path.join(GFXDIR, "sword_hit_small.gif"))
			damage = roll_attack_damage(attacker, target)
			target.take_hit(damage * attacker.mp)
			attacker.mp = 0

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

	def init_sidebar(self):
		coords = [(self.sidebar.left + 10), (self.sidebar.top + 100)]
		width = self.sidebar.width - 20
		height = self.sidebar.height - 110
		bar_height = 20
		margin = 5
		bar_size = [width, bar_height]
		players = self.get_all_players()
		for player in players:
			label = PlayerName(player, pygame.Rect(coords, (1, 1)))
			self.sprites.add(label)
			coords[1] += label.font.get_linesize()
			for character in player.all_characters:
				character_healthbar_rect = pygame.Rect(tuple(coords), tuple(bar_size))
				bar = MainHealthBar(character, character_healthbar_rect)
				self.sprites.add(bar)
				# XXX: fix character healthbars
				#if self.showhealth:
				#	draw_char_hp_bar(self.screen, pygame.Rect((character.x + 2, character.y - (CHAR_SIZE[1] - TILE_SIZE[1])), (48-4, 8)), character.max_hp, character.hp)
				coords[1] += (bar_height + margin)

class StateTrackingSprite(pygame.sprite.DirtySprite):
	def __init__(self):
		pygame.sprite.DirtySprite.__init__(self)
		self.state = None

	def get_state(self):
		raise NotImplemented, 'This method must be implemented by base classes'

	def update(self):
		if not self.visible:
			return

		state = self.get_state()
		if state == self.state:
			return

		self.redraw()
		self.dirty = 1

class Animation(pygame.sprite.DirtySprite):
	def __init__(self, character, file_path, interval = 1):
		pygame.sprite.DirtySprite.__init__(self)
		self._layer = (L_CHAR, character.grid_y, L_CHAR_EFFECT)

		self.images = iter(get_animation_surfaces(file_path))
		self.image = self.images.next()
		self.rect = character.rect

		self.interval = interval
		self.count = 0

	def update(self):
		if not self.visible:
			return

		self.count += 1
		if self.count >= self.interval:
			self.count = 0

			try:
				self.image = self.images.next()
			except StopIteration:
				self.visible = 0
			else:
				self.dirty = 1

class MainHealthBar(StateTrackingSprite):
	def __init__(self, character, rect):
		StateTrackingSprite.__init__(self)
		self.character = character

		self.image = pygame.Surface(rect.size)
		self.rect = rect

	def get_state(self):
		return self.character.max_hp, self.character.hp

	def redraw(self):
		draw_main_hp_bar(self.image, self.image.get_rect(), self.character.max_hp, self.character.hp)

class PlayerName(pygame.sprite.DirtySprite):
	def __init__(self, player, rect):
		pygame.sprite.DirtySprite.__init__(self)
		self.player = player

		self.font = pygame.font.Font(FONT, int(20*FONTSCALE))

		self.image = self.font.render(self.player.name, True, (255,255, 255))
		self.rect = self.image.get_rect()
		self.rect.topleft = rect.topleft

class CurrentPlayerName(pygame.sprite.DirtySprite):
	def __init__(self, main, centerx):
		pygame.sprite.DirtySprite.__init__(self)
		self.centerx = centerx
		self.main = main
		self.text = None

		self.font = pygame.font.Font(FONT, int(50*FONTSCALE))

	def update(self):
		text = self.main.current_player.name
		if text == self.text:
			return

		self.dirty = 1
		self.text = text

		self.image = self.font.render(self.text, True, (255,255, 255))
		self.rect = self.image.get_rect()
		self.rect.centerx = self.centerx
		self.rect.centery = 50

class DisabledCharacter(pygame.sprite.DirtySprite):
	def __init__(self, main, character):
		pygame.sprite.DirtySprite.__init__(self)
		self.character = character
		self.main = main

		self.image = self.rect = None
		self.update()

	_layer = property(lambda self: (L_CHAR, self.character.grid_y, L_CHAR_OVERLAY), lambda self, value: None)

	def update(self):
		try:
			image = self.main.disabled_chartypes[self.character.race.name][self.character.heading]
		except:
			image = self.main.chartypes[self.character.race.name][self.character.heading].convert_alpha()
			image.fill((0, 0, 0, 200), special_flags=pygame.BLEND_RGBA_MULT)
			self.main.disabled_chartypes.setdefault(self.character.race.name, {})[self.character.heading] = image

		self.visible = self.character.visible and self.character.player != self.main.current_player
		if image != self.image or self.character.rect != self.rect:
			self.dirty = 1

		self.image = image
		self.rect = self.character.rect

class Fps(pygame.sprite.DirtySprite):
	def __init__(self, clock, centerx):
		pygame.sprite.DirtySprite.__init__(self)
		self.centerx = centerx
		self.clock = clock
		self.font = pygame.font.Font(FONT, int(20*FONTSCALE))
		self.hue = 0

		self.dirty = 2

	def update(self):
		self.hue += 10

		# XXX: less flashy way to indicate that we're running smoothly
		color = get_hue_color(self.hue)
		fps = self.clock.get_fps()

		self.image = self.font.render('fps: %d' % fps, True, color)
		self.rect = self.image.get_rect()
		self.rect.centerx = self.centerx

class SpriteGrid:
	def __init__(self, grid, tile):
		self.sprites = pygame.sprite.Group()
		for i in range(len(grid)):
			self.sprites.add(Tile(tile, pygame.Rect(grid[i][0]*TILE_SIZE[0], grid[i][1]*TILE_SIZE[1], *TILE_SIZE), layer = (L_SEL, )))

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
			self.sprites.add(Tile(tile, pygame.Rect(x*TILE_SIZE[0], y*TILE_SIZE[1], *TILE_SIZE), layer = (L_MAP, y)))

	def get_map(self):
		return self.map

class Player:
	"""Class to create player or team in the game. One player may have many characters."""
	def __init__(self, name, chardata, main):
		self.name = name
		self.main = main
		self.all_characters = [CharacterSprite(self, race_name, 5, (x, y), heading, main) for race_name, x, y, heading in chardata]

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

def roll_attack_damage(attacker, defender):
	attacker_miss_chance = attacker.per_wc_miss_chance.get(attacker.weapon.class_, 10) - attacker.weapon.magic_enchantment * 2
	defender_evasion_chance = defender.terrain_miss_chance + defender.armor.miss_chance + math.floor(defender.dexterity / 5)
	miss_chance = attacker_miss_chance + defender_evasion_chance
	is_hit = random.randrange(100) < 100 - miss_chance
	print 'Miss chance:', miss_chance
	if not is_hit:
		print 'Missed!'
		return 0

	is_critical_hit = random.randrange(100) < attacker.weapon.critical_chance

	print 'Critical chance and multiplier:', attacker.weapon.critical_chance, attacker.weapon.critical_multiplier
	if is_critical_hit: print 'Critical!'
	damage_multiplier = attacker.weapon.critical_multiplier if is_critical_hit else 1

	wc_damage = {'melee': attacker.strength, 'ranged': attacker.dexterity, 'magic': attacker.intelligence}[attacker.weapon.type]
	weapon_damage = attacker.weapon.damage.roll()
	print attacker.weapon, 'rolled', weapon_damage, 'of', 'damage'

	# XXX: Magic should bypass damage reduction
	positive_damage = damage_multiplier * (weapon_damage + wc_damage + attacker.weapon.magic_enchantment)#+ attacker.class_(passive)_skill.damage # XXX Alexer: add passive skill damage
	negative_damage = defender.class_damage_reduction + math.floor(defender.constitution / 10) + defender.armor.damage_reduction
	if not attacker.weapon.damage_type - defender.armor.enchanted_damage_reduction_type:
		print 'Armor negates', defender.armor.enchanted_damage_reduction, 'of the weapon\'s', '/'.join(defender.armor.enchanted_damage_reduction_type), 'damage'
		negative_damage += defender.armor.enchanted_damage_reduction
	damage = positive_damage - negative_damage # XXX Alexer: no total negative allowed

	print positive_damage, 'of damage and', negative_damage, 'of damage reduction: dealt', damage, 'of damage'

	return int(math.floor(max(damage, 0)))

class Character:
	def __init__(self, name, race_name, class_name, str, dex, con, int):
		self.race = races[race_name]
		self.class_ = None
		self.str = 1 + self.race.base_str + str
		self.dex = 1 + self.race.base_dex + dex
		self.con = 1 + self.race.base_con + con
		self.int = 1 + self.race.base_int + int

		self.max_hp = self.con * 10
		self.max_sp = self.int
		self.max_mp = self.dex

	@classmethod
	def random(cls):
		rndstats = [random.choice(['dex', 'con', 'int', 'str']) for i in range(random.randrange(4, 6+1))]
		str = rndstats.count('str')
		dex = rndstats.count('dex')
		con = rndstats.count('con')
		int = rndstats.count('int')
		return cls(None, random.choice(races.keys()), None, str, dex, con, int)

class CharacterSprite(UIGridObject, pygame.sprite.DirtySprite):
	"""Universal class for any character in the game"""
	def __init__(self, player, race_name, max_mp, coords, heading, main, max_hp = 100, attack_stat = 10):
		UIGridObject.__init__(self, main.map, coords)
		pygame.sprite.DirtySprite.__init__(self)

		self.player = player
		self.race = races[race_name]
		# Movement points
		self.max_mp = max_mp
		self.mp = max_mp
		# Health points
		self.max_hp = max_hp
		self.hp = max_hp
		# Stats
		rndstats = [random.choice(['dex', 'con', 'int', 'str']) for i in range(random.randrange(4, 6+1))]
		self.dexterity = self.race.base_dex + rndstats.count('dex')
		self.constitution = self.race.base_con + rndstats.count('con')
		self.intelligence = self.race.base_int + rndstats.count('int')
		self.strength = self.race.base_str + rndstats.count('str')
		# Status
		self.heading = heading   # Angle from right to counter-clockwise in degrees, possible values are: 0, 45, 90, 135, 180, 225, 270 and 315
		self.selected = False
		self.alive = True

		self.terrain_miss_chance = 0 # XXX Alexer: lolfixthis :D
		self.per_wc_miss_chance = {}
		self.class_damage_reduction = random.randrange(3)
		self.armor = Armor.random()
		self.weapon = random.choice(weapons.values())#Weapon.random()

		self.main = main
		self.background_map = self.main.map.get_map()
		self.walkable_tiles = self.main.walkable
		self.players = self.main.get_all_players()

	def _get_rect(self): return pygame.Rect(self.x, self.y - (CHAR_SIZE[1] - TILE_SIZE[1]), *CHAR_SIZE)
	rect = property(_get_rect)

	_layer = property(lambda self: (L_CHAR, self.grid_y), lambda self, value: None)

	def update(self):
		self.image = self.main.chartypes[self.race.name][self.heading]
		self.dirty = 1

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

class Tile(pygame.sprite.DirtySprite):
	def __init__(self, image, rect=None, layer=0):
		pygame.sprite.DirtySprite.__init__(self)
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
