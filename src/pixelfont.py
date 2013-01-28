import os
import pygame
import Image, ImageDraw, ImageFont
from config import *

def draw_pixel_text(text, scale = 1, color = (0, 0, 0)):
	font = ImageFont.FreeTypeFont(os.path.join(FONTDIR, 'pf_tempesta_five_condensed.ttf'), 8)
	width = font.getsize(text)[0]
	im = Image.new('1', (width, 15))
	draw = ImageDraw.Draw(im)
	draw.rectangle(((0, 0), (width, 15)), fill=1)
	draw.text((0, 0), text, font=font, fill=0)
	bw = im.crop((0, 3, width, 10))
	im = bw.convert('RGB')

	if color != (0, 0, 0):
		mask = bw.point(lambda v: 1 - v, '1')
		im.paste(color, (0, 0) + mask.size, mask)

	text = pygame.image.fromstring(im.tostring(), im.size, im.mode)
	text.set_colorkey((255, 255, 255))

	if scale != 1:
		rect = text.get_rect()
		text = pygame.transform.scale(text, (scale * rect.width, scale * rect.height))

	return text

def draw_speech_bubble(text):
	text = draw_pixel_text(text)
	rect = text.get_rect()
	rect.topleft = (3, 2)
	width, height = size = max(3 + rect.width + 2, 13), max(2 + rect.height + 2 + 4, 10)
	bubble = pygame.Surface(size)
	# Transparency
	bubble.set_colorkey((255, 0, 255))
	bubble.fill((255, 0, 255))
	# Inside of the bubble
	bubble.fill((255, 255, 255), (1, 1, width - 2, height - 6))
	# Borders of the bubble
	bubble.fill((0, 0, 0), (0, 2, 1, height - 8))
	bubble.fill((0, 0, 0), (width - 1, 2, 1, height - 8))
	bubble.fill((0, 0, 0), (2, 0, width - 4, 1))
	bubble.fill((0, 0, 0), (2, height - 5, width - 4, 1))
	# Corners of the bubble
	bubble.fill((0, 0, 0), (1, 1, 1, 1))
	bubble.fill((0, 0, 0), (width - 2, 1, 1, 1))
	bubble.fill((0, 0, 0), (1, height - 6, 1, 1))
	bubble.fill((0, 0, 0), (width - 2, height - 6, 1, 1))
	# Inside of the jag
	bubble.fill((255, 255, 255), (5, height - 5, 3, 3))
	bubble.fill((255, 0, 255), (7, height - 3, 1, 1))
	# Border of the jag
	bubble.fill((0, 0, 0), (4, height - 5, 1, 4))
	bubble.fill((0, 0, 0), (5, height - 2, 1, 1))
	bubble.fill((0, 0, 0), (6, height - 3, 1, 1))
	bubble.fill((0, 0, 0), (7, height - 4, 1, 1))
	# Text
	bubble.blit(text, rect)
	rect = bubble.get_rect()
	bubble = pygame.transform.scale(bubble, (SCALE * rect.width, SCALE * rect.height))
	return bubble

