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
		
		self.parent_buttons = []
		parent_button = Func_Button(50, 50, 75, 20, 2, (200, 200, 200), (50, 50, 50), [["Click here", None]], None, 20, self.screen, self.enable_buttons, True)
		child_button1 = Func_Button(50, 20, 75, 20, 2, (200, 200, 200), (50, 50, 50), [["Test1", None]], None, 20, self.screen, self.button_click, False)
		child_button2 = Func_Button(50, 80, 75, 20, 2, (200, 200, 200), (50, 50, 50), [["Test2", None]], None, 20, self.screen, self.button_click, False)
		self.parent_buttons.append([parent_button, child_button1, child_button2])
		
		icon = pygame.image.load(os.path.join(GFXDIR, "test_icon.png"))
		parent_button = Func_Button(200, 50, 52, 52, 2, (200, 200, 200), (50, 50, 50), None, [[icon, (4, 4)]], 20, self.screen, self.enable_buttons, True)
		child_button1 = Func_Button(200, 24, 50, 20, 2, (200, 200, 200), (50, 50, 50), [["Equip", None]], None, 20, self.screen, self.button_click, False)
		child_button2 = Func_Button(200, 108, 50, 20, 2, (200, 200, 200), (50, 50, 50), [["Sell", None]], None, 20, self.screen, self.button_click, False)
		self.parent_buttons.append([parent_button, child_button1, child_button2])
		
		icon = pygame.image.load(os.path.join(GFXDIR, "test_icon.png"))
		parent_button = Func_Button(300, 50, 78, 75, 2, (200, 200, 200), (50, 50, 50), [["Mighty Sword", (5, 55)]], [[icon, (15,4)]], 15, self.screen, self.enable_buttons, True)
		child_button1 = Func_Button(300, 16, 78, 28, 2, (200, 200, 200), (50, 50, 50), [["Equip", None]], None, 25, self.screen, self.button_click, False)
		child_button2 = Func_Button(300, 131, 78, 28, 2, (200, 200, 200), (50, 50, 50), [["Sell", None]], None, 25, self.screen, self.button_click, False)
		self.parent_buttons.append([parent_button, child_button1, child_button2])
		
	def button_click(self):
		print "Clicked button"
		
	def enable_buttons(self, i):
		for b in range(1, len(self.parent_buttons[i])):
			self.parent_buttons[i][b].toggle_visibility()

	def loop(self):
		while 1:
			self.screen.fill((127, 127, 127))
			for p in self.parent_buttons:
				for c in p:
					if c.enabled: c.draw()
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						for p in range(0, len(self.parent_buttons)):
							for c in range(0, len(self.parent_buttons[p])):
								if self.parent_buttons[p][c].enabled:
									if self.parent_buttons[p][c].contains(*event.pos):
										f = self.parent_buttons[p][c].get_function()
										if c == 0: #First on list is parent button
											f(p)
										else:
											f()
				elif event.type == pygame.QUIT:
					sys.exit()

			time.sleep(0.05)
			
if __name__ == "__main__":
	win = UItest()
	win.loop()