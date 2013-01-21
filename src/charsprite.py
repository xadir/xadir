import pygame
from config import *
from UI import UIGridObject


class CharacterSprite(UIGridObject, pygame.sprite.DirtySprite):
	"""Universal class for any character in the game"""
	def __init__(self, player, character, coords, heading, map, res):
		UIGridObject.__init__(self, self.map, coords)
		pygame.sprite.DirtySprite.__init__(self)

		self.player = player
		self.char = character
		# Movement points
		self.mp = self.max_mp
		# Health points
		self.hp = self.max_hp
		# Status
		self.heading = heading   # Angle from right to counter-clockwise in degrees, possible values are: 0, 45, 90, 135, 180, 225, 270 and 315
		self.map = map
		self.selected = False
		self.alive = True

		self.terrain_miss_chance = 0 # XXX Alexer: lolfixthis :D

		self.res = res

	def __getattr__(self, name):
		return getattr(self.char, name)

	def _get_rect(self): return pygame.Rect(self.x, self.y - (CHAR_SIZE[1] - TILE_SIZE[1]), *CHAR_SIZE)
	rect = property(_get_rect)

	_layer = property(lambda self: L_CHAR(self.grid_y), lambda self, value: None)

	def update(self):
		self.image = self.res.races[self.race.name][self.heading]
		self.dirty = 1

	def is_selected(self):
		return self.selected

	def take_hit(self, attack_points):
		print 'Took', attack_points, 'of damage'
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

