import pygame
from config import *
from resources import blitteds
from UI import UIGridObject

class CharacterSprite(UIGridObject, pygame.sprite.DirtySprite):
	"""Universal class for any character in the game"""
	def __init__(self, player, character, coords, heading, map, res):
		UIGridObject.__init__(self, map, coords)
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

		self.res = res

		self.update()

	def __getattr__(self, name):
		return getattr(self.char, name)

	def _get_rect(self): return pygame.Rect(self.x - self.offset[0], self.y - self.offset[1] - (CHAR_SIZE[1] - TILE_SIZE[1]), *self.image.get_size())
	rect = property(_get_rect)

	_layer = property(lambda self: L_CHAR(self.grid_y), lambda self, value: None)

	def get_current_state(self):
		return (self.heading, self.race.name, self.char.hair_name, self.char.armor and self.char.armor.style)

	def get_current_image(self):
		image = self.res.races[self.race.name][self.heading]
		extras = []
		if self.char.hair_name:
			extras.append((self.res.hairs[self.char.hair_name][self.heading], ((CHAR_SIZE[0] - HAIR_SIZE[0]) / 2 + self.char.hair.xoffset * SCALE, ((self.race.hairline or 0) + self.char.hair.yoffset) * SCALE)))
		if self.race.armorsize and self.char.armor and self.char.armor.style:
			extras.append((self.res.armors[self.char.armor.style][self.race.armorsize][self.heading], (0, CHAR_SIZE[1] - ARMOR_SIZE[1])))
		if extras:
			image, topleft = blitteds(image, extras, copy = True)
		else:
			topleft = (0, 0)
		# Image depends on:
		# Primary: (self.heading, self.race.name, self.char.hair_name, self.char.armor and self.char.armor.style)
		# Secondary: self.race.hairline, self.char.hair.xoffset, self.char.hair.yoffset, self.race.armorsize
		return image, topleft

	def update(self):
		self.image, self.offset = self.get_current_image()
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

