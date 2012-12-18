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
from race import races, Race
from armor import armors, Armor, default as default_armor
from weapon import weapons, Weapon, default as default_weapon
from charclass import classes, CharacterClass
from character import Character

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

# XXX: Trees don't occlude characters below them since drawing selections would be a pain in the ass.
#      If we do it, trees occlude selections too...
L_MAP =          lambda y: (0, y)
L_SEL =          lambda y: (1, )
L_CHAR =         lambda y: (2, y)
L_CHAR_OVERLAY = lambda y: (2, y, 0)
L_CHAR_EFFECT =  lambda y: (2, y, 1)
L_GAMEOVER =     (3, )

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
	def __init__(self, screen, mapname='map_new.txt'):
		pygame.display.set_caption('Xadir')
		self.mapname = mapname
		self.screen = screen
		self.width, self.height = self.screen.get_size()
		self.background = pygame.Surface((self.width, self.height))
		self.background.fill((159, 182, 205))
		self.sidebar = pygame.Rect(960, 0, 240, 720)
		self.buttons = []
		self.clock = pygame.time.Clock()
		self.fps = 30
		self.showhealth = False
		self.buttons.append(Button(980, 600, 200, 100, "End turn", 40, self.next_turn))

		self.disabled_chartypes = {}

		self.messages = Messages(980, 380, 200, 200)

		self.sprites = pygame.sprite.LayeredDirty(_time_threshold = 1000.0)
		self.sprites.add(Fps(self.clock, self.sidebar.centerx))
		self.sprites.add(CurrentPlayerName(self, self.sidebar.centerx))
		self.sprites.add(self.buttons)
		self.sprites.add(self.messages)

	current_player = property(lambda self: self.players[self.turn])
	live_players = property(lambda self: [player for player in self.players if player.is_alive()])

	def load_resources(self):
		self.terrain = load_named_tiles('tilemap_terrain', TILE_SIZE, (255, 0, 255), SCALE)
		self.terrain = {'G': [self.terrain['G']], 'D': [self.terrain['D']], 'F': [self.terrain['G']], 'W': [self.terrain['W[1]'], self.terrain['W[2]']]}
		self.borders = load_named_tiles('tilemap_borders', BORDER_SIZE, (255, 0, 255), SCALE)
		self.overlay = load_named_tiles('tilemap_overlay', OVERLAY_SIZE, (255, 0, 255), SCALE)
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

		self.load_sprites()

	def main_loop(self):
		self.init_sidebar()

		change_sound(pygame.mixer.Channel(0), load_sound('battle.ogg'), BGM_FADE_MS)

		while 1:
			self.draw()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						for b in self.buttons:
							if b.contains(*event.pos):
								b.function()
						self.click()
				if event.type == KEYDOWN and event.key == K_SPACE:
					self.next_turn()
			if self.players[self.turn].movement_points_left() < 1:
				self.next_turn()
			if len(self.live_players) <= 1:
				self.gameover()

	def gameover(self):
		change_sound(pygame.mixer.Channel(0), load_sound('menu.ogg'), BGM_FADE_MS)
		if len(self.live_players) < 1:
			text = 'Draw!'
		else:
			text = '%s wins!' % self.live_players[0].name
		sprite = Textile(text, pygame.Rect((0, 0, 960, 720)), layer = L_GAMEOVER)
		self.sprites.add(sprite)
		while 1:
			self.draw()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

	def draw(self, frames = 1):
		for i in range(frames):
			self.clock.tick(self.fps)
			self.sprites.update()
			self.sprites.clear(self.screen, self.background)
			# Update layers
			self.sprites._spritelist.sort(key = lambda sprite: sprite._layer)
			self.sprites.draw(self.screen)
			pygame.display.flip()

	def load_sprites(self):
		"""Load the sprites that we need"""
		self.walkable = [name for name in self.terrain.keys() if name != 'W']
		map, mapsize, spawns = load_map(self.mapname)
		self.map = BackgroundMap(map, *mapsize, tiletypes = (self.terrain, self.borders, self.overlay))
		self.spawns = spawns
		self.players = []

	def get_random_teams(self, player_count = 2, character_count = 3):
		player_names = random.sample('Alexer Zokol brenon Prototailz Ren'.split(), player_count)
		teams = []
		for name in player_names:
			characters = []
			for i in range(character_count):
				char = Character.random()
				char.race = races[random.choice(self.chartypes.keys())]
				characters.append(char)
			teams.append((name, characters))
		return teams

	def init_teams(self, teams):
		player_ids = random.sample(self.spawns, len(teams))
		for player_id, team in zip(player_ids, teams):
			name, characters = team
			spawn_points = random.sample(self.spawns[player_id], len(characters))
			self.add_player(name, [(char, x, y, 0) for char, (x, y) in zip(characters, spawn_points)])

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
		# Five steps per second
		frames = self.fps / 5
		for i in range(1, len(path) - 1):
			character.heading = self.get_heading(path[i], path[i+1])
			character.grid_pos = path[i]
			self.draw(frames)

	def animate_hit(self, character, file_path):
		anim = AnimatedEffect(character, file_path, 3)

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
		if len(self.players) < 1 or len(self.live_players) < 1:
			return

		self.turn = (self.turn + 1) % len(self.players)
		while not self.current_player.is_alive():
			self.turn = (self.turn + 1) % len(self.players)

		self.messages.messages.append('%s\'s turn' % self.current_player.name)
		self.current_player.reset_movement_points()

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
			damage, messages = roll_attack_damage(attacker, target)
			self.messages.messages.append(' '.join(messages))
			target.take_hit(damage)
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

	def redraw(self):
		raise NotImplemented, 'This method must be implemented by base classes'

	def update(self):
		if not self.visible:
			return

		state = self.get_state()
		if state == self.state:
			return
		self.state = state

		self.redraw()
		self.dirty = 1

class Messages(StateTrackingSprite):
	def __init__(self, x, y, width, height):
		StateTrackingSprite.__init__(self)

		self.image = pygame.Surface((width, height))
		self.rect = pygame.Rect((x, y, width, height))

		self.font = pygame.font.Font(FONT, int(16*FONTSCALE))

		self.messages = []

	def wrap_line(self, line):
		words = line.split()

		wrapped = []
		while words:
			fit, words = self.find_max_fit(words)
			if fit:
				wrapped.append(' '.join(fit))
			else:
				fit, rest = self.find_max_fit(words[0])
				wrapped.append(fit)
				words[0] = rest

		return wrapped

	def find_max_fit(self, words):
		fits, cuts = 0, len(words) + 1
		while fits + 1 < cuts:
			index = (fits + cuts) / 2
			if isinstance(words, list):
				partial = ' '.join(words[:index])
			else:
				partial = words[:index]
			width, height = self.font.size(partial)
			if width > self.rect.width:
				cuts = index
			else:
				fits = index
		return words[:fits], words[fits:]

	def cull_messages(self):
		linesize = self.font.get_linesize()
		num_lines = self.rect.height / linesize

		messages = []
		for message in self.messages:
			messages.extend(self.wrap_line(message))

		self.messages = messages[-num_lines:]

	def get_state(self):
		self.cull_messages()
		return self.messages

	def redraw(self):
		self.image.fill((127, 127, 127))
		y = 0
		for message in self.messages:
			text = self.font.render(message, True, (0, 0, 0))
			self.image.blit(text, (0, y))
			y += self.font.get_linesize()

class AnimatedSprite(pygame.sprite.DirtySprite):
	def __init__(self, images, rect, layer, interval = 1):
		pygame.sprite.DirtySprite.__init__(self)
		self._layer = layer

		self.images = images
		self.pos = 0

		self.image = self.images[self.pos]
		self.rect = rect

		self.interval = interval
		self.count = 0

	def update(self):
		if not self.visible:
			return

		# Do not bother to do anything if there's no animation
		if len(self.images) <= 1:
			return

		self.count += 1
		if self.count >= self.interval:
			self.count = 0
			self.pos += 1
			if self.pos >= len(self.images):
				self.pos = 0

			self.image = self.images[self.pos]
			self.dirty = 1

class AnimatedEffect(AnimatedSprite):
	def __init__(self, character, file_path, interval = 1):
		images = list(get_animation_surfaces(file_path))
		rect = character.rect
		layer = L_CHAR_EFFECT(character.grid_y)

		AnimatedSprite.__init__(self, images, rect, layer, interval)

	def update(self):
		AnimatedSprite.update(self)

		if self.pos == 0 and self.count == 0:
			self.visible = 0

class AnimatedTile(AnimatedSprite):
	pass

class MainHealthBar(StateTrackingSprite):
	def __init__(self, character, rect):
		StateTrackingSprite.__init__(self)
		self.character = character

		self.image = pygame.Surface(rect.size)
		self.rect = rect

		self.font = pygame.font.Font(FONT, int(20*FONTSCALE))

	def get_state(self):
		return self.character.max_hp, self.character.hp

	def redraw(self):
		draw_main_hp_bar(self.image, self.image.get_rect(), self.character.max_hp, self.character.hp)

		text = self.font.render('%d/%d' % (self.character.hp, self.character.max_hp), True, (127, 127, 255))
		rect = text.get_rect()
		pos = ((self.rect.width - rect.width) / 2, (self.rect.height - rect.height) / 2)
		self.image.blit(text, pos)

class PlayerName(pygame.sprite.DirtySprite):
	def __init__(self, player, rect):
		pygame.sprite.DirtySprite.__init__(self)
		self.player = player

		self.font = pygame.font.Font(FONT, int(20*FONTSCALE))

		self.image = self.font.render(self.player.name, True, (255,255, 255))
		self.rect = self.image.get_rect()
		self.rect.topleft = rect.topleft

class CurrentPlayerName(StateTrackingSprite):
	def __init__(self, main, centerx):
		StateTrackingSprite.__init__(self)
		self.centerx = centerx
		self.main = main

		self.font = pygame.font.Font(FONT, int(50*FONTSCALE))

	def get_state(self):
		return self.main.current_player.name

	def redraw(self):
		self.image = self.font.render(self.state, True, (255,255, 255))
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

	_layer = property(lambda self: L_CHAR_OVERLAY(self.character.grid_y), lambda self, value: None)

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
			self.sprites.add(Tile(tile, pygame.Rect(grid[i][0]*TILE_SIZE[0], grid[i][1]*TILE_SIZE[1], *TILE_SIZE), layer = L_SEL(grid[i][1])))

clamp = lambda v, minv, maxv: min(max(v, minv), maxv)
clamp_r = lambda v, minv, maxv: min(max(v, minv), maxv - 1)

class BackgroundMap(Grid):
	"""Map class to create the background layer, holds any static and dynamical elements in the field."""
	def __init__(self, map, width, height, tiletypes):
		Grid.__init__(self, width, height, map)
		self.terrain, self.borders, self.overlay = tiletypes
		self.images = {}
		self.cell_size = TILE_SIZE
		self.x = self.y = 0
		self.map = self
		self.sprites = pygame.sprite.LayeredUpdates()
		for x, y in self.map.keys():
			tiles = self.get_real_tile((x, y))
			rect = tiles[0].get_rect()
			rect.top = y*TILE_SIZE[1] - (rect.height - TILE_SIZE[1])
			rect.left = x*TILE_SIZE[0]
			self.sprites.add(AnimatedTile(tiles, rect, layer = L_MAP(y), interval = 30/2))

	def get_repeated(self, (x, y)):
		return self[clamp_r(x, 0, self.width), clamp_r(y, 0, self.height)]

	def get_repeated_base(self, pos):
		tile = self.get_repeated(pos)
		if tile == 'F':
			return 'G'
		return tile

	def get_border(self, (x, y), side, tile):
		dirs = {'t': -1, 'b': 1, 'l': -1, 'r': 1, 'm': 0}
		hd, vd = dirs[side[1]], dirs[side[0]]
		d = (hd, vd)
		c = self.get_repeated_base((x + hd, y + vd)) != tile
		if 'm' in side:
			if c: return side.replace('m', ''), d
			return None, d
		h = self.get_repeated_base((x + hd, y)) != tile
		v = self.get_repeated_base((x, y + vd)) != tile
		if h and v: return '_'.join(side), d
		if h: return side[1], d
		if v: return side[0], d
		if c: return side, d
		return None, d

	def get_overlay(self, (x, y), tile):
		l = self.get_repeated((x - 1, y)) == tile
		r = self.get_repeated((x + 1, y)) == tile
		if l and r: return 'h'
		if l: return 'l'
		if r: return 'r'
		return 'm'

	def get_real_tile(self, pos):
		real_tile = tile = self[pos]
		if tile == 'F':
			tile = 'G'
		if tile in ('W', 'D'):
			borders = tuple(self.get_border(pos, side, tile) for side in 'tl tm tr ml mr bl bm br'.split())
		else:
			borders = ()
		name = (tile, borders)
		images = self.images.get(name)
		if not images:
			images = self.terrain[tile]
			if any(b for b, d in borders):
				orig_images = images
				images = []
				for image in orig_images:
					image = image.copy()
					for b, d in borders:
						if not b:
							continue
						border = self.borders[tile + '-' + b]
						image.blit(border, (((d[0] + 1) * BORDER_SIZE[0], (d[1] + 1) * BORDER_SIZE[1]), BORDER_SIZE))
					images.append(image)
				self.images[name] = images
		if real_tile == 'F':
			overlay_tile = real_tile + '-' + self.get_overlay(pos, real_tile)
			name = (tile, borders, overlay_tile)
			images2 = self.images.get(name)
			if not images2:
				orig_images = images
				images = []
				for orig_image in orig_images:
					image = pygame.Surface(OVERLAY_SIZE)
					image.fill((255, 0, 255))
					image.set_colorkey((255, 0, 255))
					image.blit(orig_image, ((0, OVERLAY_SIZE[1] - TILE_SIZE[1]), TILE_SIZE))
					overlay = self.overlay[overlay_tile]
					image.blit(overlay, ((0, 0), OVERLAY_SIZE))
					images.append(image)
				self.images[name] = images
			else:
				images = images2
		return images

	def get_map(self):
		return self.map

class Player:
	"""Class to create player or team in the game. One player may have many characters."""
	def __init__(self, name, chardata, main):
		self.name = name
		self.main = main
		self.all_characters = [CharacterSprite(self, character, (x, y), heading, main) for character, x, y, heading in chardata]

	characters = property(lambda self: [character for character in self.all_characters if character.is_alive()])
	dead_characters = property(lambda self: [character for character in self.all_characters if not character.is_alive()])

	def is_alive(self):
		return bool(self.characters)

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
	messages = []

	attacker_weapon = attacker.weapon or default_weapon
	defender_armor = defender.armor or default_armor

	attacker_miss_chance = attacker.per_wc_miss_chance.get(attacker_weapon.class_, 10) - attacker_weapon.magic_enchantment * 2
	defender_evasion_chance = defender.terrain_miss_chance + defender_armor.miss_chance + math.floor(defender.dex / 5)
	miss_chance = attacker_miss_chance + defender_evasion_chance
	hit_chance = 100 - miss_chance
	is_hit = random.randrange(100) < hit_chance

	messages.append('Hit chance is %d%%...' % hit_chance)
	if not is_hit:
		messages.append('Missed!')
		return 0, messages

	is_critical_hit = random.randrange(100) < attacker_weapon.critical_chance

	if is_critical_hit:
		messages.append('Critical hit!')
		messages.append('%.1fx damage!' % attacker_weapon.critical_multiplier)
	else:
		messages.append('Hit!')
	damage_multiplier = attacker_weapon.critical_multiplier if is_critical_hit else 1

	wc_damage = {'melee': attacker.str, 'ranged': attacker.dex, 'magic': attacker.int}[attacker_weapon.type]
	weapon_damage = attacker_weapon.damage.roll()

	messages.append('%s does %d+%d of %s damage on top of %d base damage.' % ((attacker_weapon.name or 'weapon').capitalize(), weapon_damage, attacker_weapon.magic_enchantment, '/'.join(attacker_weapon.damage_type), wc_damage))
	messages.append('%s negates %d of the damage on top of %d base damage reduction' % ((defender_armor.name or 'armor').capitalize(), defender_armor.damage_reduction, defender.class_.damage_reduction + math.floor(defender.con / 10)))

	# XXX: Magic should bypass damage reduction
	positive_damage = damage_multiplier * (weapon_damage + wc_damage + attacker_weapon.magic_enchantment)#+ attacker.class_(passive)_skill.damage # XXX Alexer: add passive skill damage
	negative_damage = defender.class_.damage_reduction + math.floor(defender.con / 10) + defender_armor.damage_reduction
	if not attacker_weapon.damage_type - defender_armor.enchanted_damage_reduction_type:
		messages[-1] += ' and %d of the weapon\'s %s damage.' % (defender_armor.enchanted_damage_reduction, '/'.join(defender_armor.enchanted_damage_reduction_type))
		negative_damage += defender_armor.enchanted_damage_reduction
	else:
		messages[-1] += '.'
	damage = positive_damage - negative_damage
	damage = int(math.floor(max(damage, 0)))

	messages.append('Total %d damage and %d damage reduction: Dealt %d damage.' % (positive_damage, negative_damage, damage))

	return damage, messages

class CharacterSprite(UIGridObject, pygame.sprite.DirtySprite):
	"""Universal class for any character in the game"""
	def __init__(self, player, character, coords, heading, main):
		UIGridObject.__init__(self, main.map, coords)
		pygame.sprite.DirtySprite.__init__(self)

		self.player = player
		self.char = character
		# Movement points
		self.mp = self.max_mp
		# Health points
		self.hp = self.max_hp
		# Status
		self.heading = heading   # Angle from right to counter-clockwise in degrees, possible values are: 0, 45, 90, 135, 180, 225, 270 and 315
		self.selected = False
		self.alive = True

		self.terrain_miss_chance = 0 # XXX Alexer: lolfixthis :D

		self.main = main
		self.background_map = self.main.map.get_map()
		self.walkable_tiles = self.main.walkable
		self.players = self.main.get_all_players()

	def __getattr__(self, name):
		return getattr(self.char, name)

	def _get_rect(self): return pygame.Rect(self.x, self.y - (CHAR_SIZE[1] - TILE_SIZE[1]), *CHAR_SIZE)
	rect = property(_get_rect)

	_layer = property(lambda self: L_CHAR(self.grid_y), lambda self, value: None)

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

class Textile(Tile): # hehehehehe
	def __init__(self, text, area_rect, layer):
		font = pygame.font.Font(FONT, int(150*FONTSCALE))
		image = font.render(text, True, (0, 0, 0))
		rect = image.get_rect()
		rect.center = area_rect.center

		Tile.__init__(self, image, rect, layer)

class Button(UIComponent, pygame.sprite.DirtySprite):
	def __init__(self, x, y, width, height, text, fontsize, function):
		UIComponent.__init__(self, x, y, width, height)
		pygame.sprite.DirtySprite.__init__(self)

		self.image = pygame.Surface(self.size)

		font = pygame.font.Font(FONT, int(fontsize*FONTSCALE))
		image = font.render(text, True, (0, 0, 0), (139, 162, 185))
		rect = image.get_rect()

		self.image.fill((139, 162, 185))
		self.image.blit(image, (self.width/2 - rect.centerx, self.height/2 - rect.centery))

		self.function = function

def start_game(mapname):
	screen = init_pygame()

	game = XadirMain(screen, mapname = mapname)
	game.load_resources()
	game.init_teams(game.get_random_teams())
	game.main_loop()

if __name__ == "__main__":
	start_game('map_new.txt')
