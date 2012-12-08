import sys, time
import pygame
from resources import *
from UI import *

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

class UItest:

	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((600, 600))
		icon = pygame.image.load(os.path.join(GFXDIR, "test_icon.png"))

		
		
		self.manage = UIContainer(None, (20, 20), (300, 250), self.screen)
		self.party = UIContainer(None, (400, 20), (126, 200), self.screen)
		self.inventory = UIContainer(None, (400, 240), (126, 200), self.screen)

		self.add_icon(icon, self.inventory)
		self.add_icon(icon, self.inventory)
		self.add_icon(icon, self.inventory)
		self.add_icon(icon, self.inventory)
		self.add_icon(icon, self.inventory)
		self.add_icon(icon, self.inventory)

		self.add_icon(icon, self.party)
		self.add_icon(icon, self.party)
		self.add_icon(icon, self.party)
		self.add_icon(icon, self.party)
			

	def add_icon(self, icon, container):
		icon_rect = icon.get_rect()
		img_width = icon_rect.width
		img_height = icon_rect.height
		icon_width = (ICON_BORDER + ICON_PADDING + img_width + ICON_PADDING + ICON_BORDER) # To clarify to layout
		icon_height = (ICON_BORDER + ICON_PADDING + img_height + ICON_PADDING + ICON_BORDER)
		icon_num = len(container.children)
		icon_place = [0,0]
		icon_place[0] = (icon_num % (container.width / icon_width))
		icon_place[1] = (icon_num / (container.width / icon_width))
		x = (ICON_MARGIN * 2) + (icon_place[0] * (ICON_MARGIN + icon_width))
		y = (ICON_MARGIN * 2) + (icon_place[1] * (ICON_MARGIN + icon_height))
		
		tmp = CascadeButton(container, self.screen, x, y, img_width + (ICON_PADDING * 2), img_height + (ICON_PADDING * 2), None, [[icon, None]])
		tmp.add_button((0, img_height + (ICON_PADDING * 2)), (img_width+ (ICON_PADDING * 2), 30), [["Sell", None]], None, self.sell, False, False, None)
		tmp.add_button((0, -32), (img_width+ (ICON_PADDING * 2), 30), [["Equip", None]], None, self.equip, False, False, None)
		container.children.append(tmp)
		
	def button_click(self):
		print "Clicked button"

	def sell(self):
		print "Item sold"

	def equip(self):
		print "Item equipped"
	
	def enable_buttons(self, i):
		for b in range(1, len(self.parent_buttons[i])):
			self.parent_buttons[i][b].toggle_visibility()
	
	def click(self, event, container):
		for b in container.children:

			if b.parent_button.contains(*event.pos):
				b.parent_button.toggle()
				b.enable_buttons()
				break
			else:
				for c in b.child_buttons:
					if c.contains(*event.pos):
						c.function()

	def loop(self):
		while 1:
			self.screen.fill((127, 127, 127))
			self.manage.draw()
			self.party.draw()
			self.inventory.draw()
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						self.click(event, self.inventory)
						self.click(event, self.party)
						self.click(event, self.manage)
				elif event.type == pygame.QUIT:
					sys.exit()

			time.sleep(0.05)
			
if __name__ == "__main__":
	win = UItest()
	win.loop()
