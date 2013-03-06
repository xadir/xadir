# input lib
from pygame.locals import *
import pygame, string
from config import FONT, FONTSCALE

class ConfigError(KeyError): pass

class Config:
	""" A utility for configuration """
	def __init__(self, options, *look_for):
		assertions = []
		for key in look_for:
			if key[0] in options.keys(): setattr(self, key[0], options[key[0]])
			else: setattr(self, key[0], key[1])
			assertions.append(key[0])
		for key in options.keys():
			if key not in assertions: raise ConfigError(key+' not expected as option')

class Input:
	""" A text input for pygame apps """
	def __init__(self, **options):
		""" Options: x, y, font, color, restricted, maxlength, prompt """
		self.options = Config(options, ['x', 0], ['y', 0], ['font', pygame.font.Font(FONT, int(32*FONTSCALE))],
							  ['color', (0,0,0)], ['restricted', 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~ '],
							  ['maxlength', -1], ['prompt', ''], ['handle_enter', None])
		self.x = self.options.x; self.y = self.options.y
		self.font = self.options.font
		self.color = self.options.color
		self.restricted = self.options.restricted
		self.maxlength = self.options.maxlength
		self.prompt = self.options.prompt; self.value = ''
		self.shifted = False
		self._handle_enter = self.options.handle_enter

	def set_pos(self, x, y):
		""" Set the position to x, y """
		self.x = x
		self.y = y

	def set_font(self, font):
		""" Set the font for the input """
		self.font = font

	def draw(self, surface):
		""" Draw the text input to a surface """
		text = self.font.render(self.prompt+self.value, 1, self.color)
		surface.blit(text, (self.x, self.y))

	def handle_enter(self):
		if self._handle_enter:
			self._handle_enter()

	def update(self, events):
		""" Update the input based on passed events """
		for event in events:
			if event.type == KEYDOWN:
				if event.key == K_BACKSPACE: self.value = self.value[:-1]
				elif event.key == K_RETURN: self.handle_enter()
				elif event.unicode in self.restricted: self.value += event.unicode
		if len(self.value) > self.maxlength and self.maxlength >= 0: self.value = self.value[:-1]

