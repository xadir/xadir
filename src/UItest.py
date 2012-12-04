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
		
		"""
		self.parent_buttons = []
		parent_button = FuncButton(None, 50, 50, 75, 20, [["Click here", None]], None, 20, self.screen, self.enable_buttons, True, False, True)
		child_button1 = FuncButton(parent_button, 0, -30, 75, 20, [["Test1", None]], None, 20, self.screen, self.button_click, False, False, False)
		child_button2 = FuncButton(parent_button, 0, 30, 75, 20, [["Test2", None]], None, 20, self.screen, self.button_click, False, False, False)
		self.parent_buttons.append([parent_button, child_button1, child_button2])
		
		icon = pygame.image.load(os.path.join(GFXDIR, "test_icon.png"))
		parent_button = FuncButton(None, 200, 50, 52, 52, None, [[icon, (4, 4)]], 20, self.screen, self.enable_buttons, True, False, True)
		child_button1 = FuncButton(parent_button, 0, -30, 50, 20, [["Equip", None]], None, 20, self.screen, self.button_click, False, False, False)
		child_button2 = FuncButton(parent_button, 0, 30, 50, 20, [["Sell", None]], None, 20, self.screen, self.button_click, False, False, False)
		self.parent_buttons.append([parent_button, child_button1, child_button2])
		
		icon = pygame.image.load(os.path.join(GFXDIR, "test_icon.png"))
		parent_button = FuncButton(None, 300, 50, 78, 75, [["Mighty Sword", (5, 55)]], [[icon, (15,4)]], 15, self.screen, self.enable_buttons, True, False, True)
		child_button1 = FuncButton(parent_button, 0, -30, 78, 28, [["Equip", None]], None, 25, self.screen, self.button_click, False, False, False)
		child_button2 = FuncButton(parent_button, 0, 30, 78, 28, [["Sell", None]], None, 25, self.screen, self.button_click, False, False, False)
		self.parent_buttons.append([parent_button, child_button1, child_button2])
		"""
		
		self.manage = UIContainer(None, (20, 20), (300, 250), self.screen)
		self.party = UIContainer(None, (400, 20), (128, 200), self.screen)
		self.inventory = UIContainer(None, (400, 240), (128, 200), self.screen)
		
		print "Inventory icons"
		self.add_icon(icon, self.inventory)
		print "Icon 2"
		self.add_icon(icon, self.inventory)
		print "Icon 3"
		self.add_icon(icon, self.inventory)
		print "Icon 4"
		self.add_icon(icon, self.inventory)
		print "Icon 5"
		self.add_icon(icon, self.inventory)
		print "Icon 6"
		self.add_icon(icon, self.inventory)
		print "End of inventory icons"
		print "Inventory container now holds these icons: ", self.inventory.children
		print "Party container now holds these icons: ", self.party.children
		
		print "Party icons"
		self.add_icon(icon, self.party)
		self.add_icon(icon, self.party)
		self.add_icon(icon, self.party)
		self.add_icon(icon, self.party)
		print "End of party icons"
		print "Party container now holds these icons: ", self.party.children
		
	def add_icon(self, icon, container):
		print container
		icon_rect = icon.get_rect()
		img_width = icon_rect.width
		img_height = icon_rect.height
		icon_width = (ICON_BORDER + ICON_PADDING + img_width + ICON_PADDING + ICON_BORDER) # To clarify to layout
		icon_height = (ICON_BORDER + ICON_PADDING + img_height + ICON_PADDING + ICON_BORDER)
		icon_num = len(container.children)
		icon_place = [0,0]
		icon_place[0] = (icon_num % (container.width / icon_width))
		icon_place[1] = (icon_num / (container.width / icon_width))
		print "icons place in grid is: ", icon_place
		x = (ICON_MARGIN * 2) + (icon_place[0] * (ICON_MARGIN + icon_width))
		y = (ICON_MARGIN * 2) + (icon_place[1] * (ICON_MARGIN + icon_height))
		
		tmp = CascadeButton(container, self.screen, x, y, img_width + (ICON_PADDING * 2), img_height + (ICON_PADDING * 2), None, [[icon, (ICON_PADDING,ICON_PADDING)]])
		tmp.add_button((0, img_height + (ICON_PADDING * 2)), (img_width+ (ICON_PADDING * 2), 30), [["Sell", None]], None, self.button_click, False, False, None)
		tmp.add_button((0, -32), (img_width+ (ICON_PADDING * 2), 30), [["Equip", None]], None, self.button_click, False, False, None)
		container.children.append(tmp)
		
	def button_click(self):
		print "Clicked button"
	
	def enable_buttons(self, i):
		for b in range(1, len(self.parent_buttons[i])):
			self.parent_buttons[i][b].toggle_visibility()
	
	def click(self, event, container):
		for b in container.children:
			if b.parent_button.contains(*event.pos):
				print "Clicked parent button"
				b.parent_button.toggle()
				b.enable_buttons()

	def loop(self):
		while 1:
			self.screen.fill((127, 127, 127))
			"""
			for p in self.parent_buttons:
				for c in p:
					if c.visible: c.draw()
			"""
			self.manage.draw()
			self.party.draw()
			self.inventory.draw()
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						"""
						for p in range(0, len(self.parent_buttons)):
							for c in range(0, len(self.parent_buttons[p])):
								if self.parent_buttons[p][c].visible:
									if self.parent_buttons[p][c].contains(*event.pos):
										self.parent_buttons[p][c].toggle()
										f = self.parent_buttons[p][c].get_function()
										if c == 0: #First on list is parent button
											f(p)
										else:
											f()
						"""
						"""
						for c in self.test1.child_buttons:
							if c.contains(*event.pos):
								c.toggle()
								f = c.get_function()
								f()
								break
						else:
							break
						"""
						self.click(event, self.inventory)
						self.click(event, self.party)
						self.click(event, self.manage)
				elif event.type == pygame.QUIT:
					sys.exit()

			time.sleep(0.05)
			
if __name__ == "__main__":
	win = UItest()
	win.loop()