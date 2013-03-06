# input lib
from pygame.locals import *
import pygame, string
from config import FONT, FONTSCALE

DEFAULT_ALLOWED = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~ '

class Input:
	"""A text input for pygame apps"""
	def __init__(self, x = 0, y = 0, font = None, color = (0, 0, 0), restricted = DEFAULT_ALLOWED, maxlength = None, prompt = '', handle_enter = None):
		self.pos = (x, y)
		self.font = font or pygame.font.Font(FONT, int(32*FONTSCALE))
		self.color = color
		self.restricted = restricted
		self.maxlength = maxlength
		self.prompt = prompt
		self.value = ''
		self._handle_enter = handle_enter

	def draw(self, surface):
		"""Draw the text input to a surface"""
		text = self.font.render(self.prompt + self.value, 1, self.color)
		surface.blit(text, self.pos)

	def handle_enter(self):
		if self._handle_enter:
			self._handle_enter()

	def update(self, events):
		"""Update the input based on passed events"""
		for event in events:
			if event.type == KEYDOWN:
				if event.key == K_BACKSPACE:
					self.value = self.value[:-1]
				elif event.key == K_RETURN:
					self.handle_enter()
				elif event.unicode in self.restricted:
					self.value += event.unicode
		if self.maxlength is not None and len(self.value) > self.maxlength:
			self.value = self.value[:self.maxlength]

