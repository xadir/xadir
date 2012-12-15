import sys, time
import pygame
from resources import *
from game import *
from UI import *

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

class UItest:

	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((600, 720))
		icon = pygame.image.load(os.path.join(GFXDIR, "test_icon.png"))

		self.party = []
		char0 = Character("test0", "human", "Warrior", 10, 10, 10, 10)
		char1 = Character("test1", "minotaur", "Healer", 10, 10, 10, 10)
		char2 = Character("test2", "imp", "Mage", 10, 10, 10, 10)
		char3 = Character("test3", "treant", "Warrior", 10, 10, 10, 10)
		self.party.append(char0)
		self.party.append(char1)
		self.party.append(char2)
		self.party.append(char3)

		self.team = []

		self.selected_char = None

		# Array of party, each character-entity consists the race, class and equipped items
		#party = [["Medusa", "Warrior", [None]],["Human3", "Warrior", [None]],["Alien", "Warrior", [None]],["Dragon", "Warrior", [None]],["Taurus", "Warrior", [None]],["Wolf", "Warrior", [None]]]

		# Array of items that player has
		#inventory = [(icon)]

		self.manage = UIContainer(None, (20, 20), (300, 250), self.screen)
		self.party_con = UIContainer(None, (400, 20), (152, 200), self.screen)
		self.inventory = UIContainer(None, (400, 240), (152, 200), self.screen)
		self.char_inventory = UIContainer(None, (250, 20), (126, 250), self.screen)
		self.team_con = UIContainer(None, (20, 290), (354, 120), self.screen)

		self.race_sprite_x = self.manage.x + 50
		self.race_sprite_y = self.manage.y + 20
		self.manager_buttons = []
		self.manager_texts = []

		self.add_icon(icon, self.inventory)
		self.add_icon(icon, self.inventory)
		self.add_icon(icon, self.inventory)
		self.add_icon(icon, self.inventory)
		self.add_icon(icon, self.inventory)
		self.add_icon(icon, self.inventory)

		#self.add_icon(race_tile("Human").get_tile(0, 0, '270').image, self.party)
		#self.add_icon(race_tile("Human2").get_tile(0, 0, '270').image, self.party)
		#self.add_icon(race_tile("Human3").get_tile(0, 0, '270').image, self.party)
		#self.add_icon(race_tile("Alien").get_tile(0, 0, '270').image, self.party)
		#self.add_char("Medusa", self.party)
		#self.add_char("Human3", self.party)
		#self.add_char("Alien", self.party)
		#self.add_char("Dragon", self.party)
		#self.add_char("Taurus", self.party)
		#self.add_char("Wolf", self.party)
		
		self.update_char_panels()

	def update_char_panels(self):
		self.party_con.clear()
		for char in self.party:
			self.add_char(char.race.name, self.party_con, char)

		self.team_con.clear()
		for char in self.team:
			self.add_char(char.race.name, self.team_con, char)

		self.manage.clear()
		self.char_inventory.clear()
		self.manager_texts = []
		print self.selected_char
		if self.selected_char != None:
			self.race_sprite_path = RACE_SPRITES[self.selected_char.race.name]
			self.race = race_tile(self.selected_char.race.name)
			self.race_sprite = self.race.get_sprite(self.race_sprite_x, self.race_sprite_y)
			self.manage.spritegroup.add(self.race_sprite)
			self.race_tile = self.race.get_tile()
			sprite_rect = self.race_tile.rect

			# Get printable variables of the selected character: name, race_name, class_name, str, dex, con, int
			print self.selected_char.name, self.selected_char.race.name, self.selected_char.class_
			print "Str: " + str(self.selected_char.str), "Dex: " + str(self.selected_char.dex)
			print  "Con: " + str(self.selected_char.con), "Int: " + str(self.selected_char.int)

			font = pygame.font.Font(FONT, int(20*FONTSCALE))
			text = font.render(self.selected_char.name, True, COLOR_FONT, COLOR_BG)
			rect = text.get_rect()
			rect.centerx = sprite_rect.centerx
			rect.centery = self.race_sprite_y + 60
			self.manager_texts.append([text, rect])

			text = font.render(self.selected_char.race.name, True, COLOR_FONT, COLOR_BG)
			rect = text.get_rect()
			rect.centerx = sprite_rect.centerx
			rect.centery = self.race_sprite_y + 70
			self.manager_texts.append([text, rect])

			text = font.render(self.selected_char.class_, True, COLOR_FONT, COLOR_BG)
			rect = text.get_rect()
			rect.centerx = sprite_rect.centerx
			rect.centery = self.race_sprite_y + 80
			self.manager_texts.append([text, rect])

			text = font.render("Str: " + str(self.selected_char.str), True, COLOR_FONT, COLOR_BG)
			rect = text.get_rect()
			rect.centerx = sprite_rect.centerx
			rect.centery = self.race_sprite_y + 90
			self.manager_texts.append([text, rect])

			text = font.render("Dex: " + str(self.selected_char.dex), True, COLOR_FONT, COLOR_BG)
			rect = text.get_rect()
			rect.centerx = sprite_rect.centerx
			rect.centery = self.race_sprite_y + 100
			self.manager_texts.append([text, rect])

			text = font.render("Con: " + str(self.selected_char.con), True, COLOR_FONT, COLOR_BG)
			rect = text.get_rect()
			rect.centerx = sprite_rect.centerx
			rect.centery = self.race_sprite_y + 110
			self.manager_texts.append([text, rect])

			text = font.render("Int: " + str(self.selected_char.int), True, COLOR_FONT, COLOR_BG)
			rect = text.get_rect()
			rect.centerx = sprite_rect.centerx
			rect.centery = self.race_sprite_y + 120
			self.manager_texts.append([text, rect])

			for t in self.manager_texts:
				print t
				self.manage.surface.blit(t[0], t[1])

	def add_char(self, race, container, character):
		race_image = race_tile(race).get_tile(0, 0, '270').image
		cropped = pygame.Surface((36, 40))
		cropped.fill(COLOR_BG)
		cropped.blit(race_image, (0, 0), (6, 12, 36, 40))

		icon_rect = cropped.get_rect()
		img_width = icon_rect.width
		img_height = icon_rect.height
		print img_width, img_height
		icon_width = (ICON_BORDER + ICON_PADDING + img_width + ICON_PADDING + ICON_BORDER) # To clarify to layout
		icon_height = (ICON_BORDER + ICON_PADDING + img_height + ICON_PADDING + ICON_BORDER)
		icon_num = len(container.children)
		icon_place = [0,0]
		icon_place[0] = (icon_num % (container.width / icon_width))
		icon_place[1] = (icon_num / (container.width / icon_width))
		x = (ICON_MARGIN * 2) + (icon_place[0] * (ICON_MARGIN + icon_width))
		y = (ICON_MARGIN * 2) + (icon_place[1] * (ICON_MARGIN + icon_height))
		
		tmp = CascadeButton(container, self.screen, x, y, img_width + (ICON_PADDING * 2), img_height + (ICON_PADDING * 2), None, [[cropped, None]])
		tmp.add_button((0, img_height + (ICON_PADDING * 2)), (img_width+ (ICON_PADDING * 2), 30), [["Manage", None]], None, (self.char_manage, character), False, False, None)
		tmp.add_button((0, -32), (img_width+ (ICON_PADDING * 2), 30), [["Select", None]], None, (self.char_add, character), False, False, None)
		container.children.append(tmp)

	def add_icon(self, icon, container, item=None):
		icon_rect = icon.get_rect()
		img_width = icon_rect.width
		img_height = icon_rect.height
		print img_width, img_height
		icon_width = (ICON_BORDER + ICON_PADDING + img_width + ICON_PADDING + ICON_BORDER) # To clarify to layout
		icon_height = (ICON_BORDER + ICON_PADDING + img_height + ICON_PADDING + ICON_BORDER)
		icon_num = len(container.children)
		icon_place = [0,0]
		icon_place[0] = (icon_num % (container.width / icon_width))
		icon_place[1] = (icon_num / (container.width / icon_width))
		x = (ICON_MARGIN * 2) + (icon_place[0] * (ICON_MARGIN + icon_width))
		y = (ICON_MARGIN * 2) + (icon_place[1] * (ICON_MARGIN + icon_height))
		
		tmp = CascadeButton(container, self.screen, x, y, img_width + (ICON_PADDING * 2), img_height + (ICON_PADDING * 2), None, [[icon, None]])
		tmp.add_button((0, img_height + (ICON_PADDING * 2)), (img_width+ (ICON_PADDING * 2), 30), [["Sell", None]], None, (self.sell, item), False, False, None)
		tmp.add_button((0, -32), (img_width+ (ICON_PADDING * 2), 30), [["Equip", None]], None, (self.equip, [icon, item]), False, False, None)
		container.children.append(tmp)

	def new_character(self, container):
		self.race_x = container.x + 50
		self.race_y = container.y + 10

		#self.race_index = 0
		#self.hair_index = 0

		#self.races = RACE_SPRITES.keys()
		#self.current_race = self.races[self.race_index]
	
		"""
		all_hairs = RACE_HAIRS.keys()
		compatible_hairs = [(None, 0)]
		for hair in all_hairs:
			tmp = RACE_HAIRS[hair]
			for i in tmp:
				if i[0] == current_race:
					compatible_hairs.append(hair, i[1])
		print compatible_hairs
		current_hair = compatible_hairs[hair_index][0]
		current_hairline = compatible_hairs[hair_index][1]
		
		if current_hair != None:
			hair_sprite_path = HAIR_SPRITES[current_hair]
		if current_hair != None:
			self.hair_tile = hair_tile(self.races[current_race], self.hairs[current_hair]).get_tile(x, y, '270')
			self.images = [[self.race_tile, None], [self.hair_tile, None]]
		else: self.images = [[self.race_tile, None]]
		"""

		"""
		self.images = [[self.race_tile, None]]		

		print self.race_tile.rect.x, self.race_tile.rect.y

		img_width = self.race_tile.rect.width
		img_height = self.race_tile.rect.height
		"""

		if self.selected_char != None:

			self.race_sprite_path = RACE_SPRITES[self.selected_char.race.name]

			self.race = race_tile(self.selected_char.race.name)
			self.race_sprite = self.race.get_sprite(self.race_x, self.race_y)

			container.spritegroup.add(self.race_sprite)
		

		#tmp = CascadeButton(container, self.screen, x, y, 90 + (ICON_PADDING * 2), 100 + (ICON_PADDING * 2), None, self.images)

		#add_button(self, coords, size, text, image, function, visible=False, static=False, align=None)
		#FuncButton(self, parent, x, y, width, height, text, image, fontsize, surface, layer, function, visible, selected, static):
		
		#tmp.add_button((5, 5), (20, 20), [["<", None]], None, self.prev_hair, True, True, None)
		#tmp.add_button((img_width + 15 + (ICON_PADDING * 2), 5), (20, 20), [[">", None]], None, self.next_hair, True, True, None)

		"""
		prevRaceButton = FuncButton(container, 10, 40, 15, 15, [['<', None]], None, ICON_FONTSIZE, self.screen, 1, (self.prev_race, self.race_sprite), True, False, True)
		nextRaceButton = FuncButton(container, 120, 40, 15, 15, [['>', None]], None, ICON_FONTSIZE, self.screen, 1, (self.next_race, self.race_sprite), True, False, True)

		self.manager_buttons.append(prevRaceButton)
		container.spritegroup.add(prevRaceButton)

		self.manager_buttons.append(nextRaceButton)
		container.spritegroup.add(nextRaceButton)

		prevClassButton = FuncButton(container, 10, 80, 15, 15, [['<', None]], None, ICON_FONTSIZE, self.screen, 1, (self.prev_class, None), True, False, True)
		nextClassButton = FuncButton(container, 120, 80, 15, 15, [['>', None]], None, ICON_FONTSIZE, self.screen, 1, (self.next_class, None), True, False, True)

		self.manager_buttons.append(prevClassButton)
		container.spritegroup.add(prevClassButton)

		self.manager_buttons.append(nextClassButton)
		container.spritegroup.add(nextClassButton)
		"""
		#FuncButton(self.parent_button, x, y, size[0], size[1], text, image, ICON_FONTSIZE, self.surface, 1, function, visible, False, static)

		"""
		tmp.add_button((5, 30), (20, 20), [["<", None]], None, self.prev_char, True, True, None)
		tmp.add_button((img_width + 15 + (ICON_PADDING * 2), 30), (20, 20), [[">", None]], None, self.next_char, True, True, None)
		tmp.add_button((5, 60), (20, 20), [["<", None]], None, self.prev_class, True, True, None)
		tmp.add_button((img_width + 15 + (ICON_PADDING * 2), 60), (20, 20), [[">", None]], None, self.next_class, True, True, None)
		container.children.append(tmp)
		"""
				

	def button_click(self):
		print "Clicked button"

	def sell(self, item):
		print "Item sold"

	def equip(self, item):
		print "Item equipped"

	def prev_hair(self):
		print "Previous hair"
	
	def next_hair(self):
		print "Next hair"

	def prev_race(self, race_sprite):
		print "Previous race"
		self.race_index = (self.race_index - 1) % len(self.races)
		self.current_race = self.races[self.race_index]

		self.race_sprite_path = RACE_SPRITES[self.current_race]
		print self.race_index, self.current_race, self.race_sprite_path
		self.race = race_tile(self.current_race)
		self.race_sprite = self.race.get_sprite(self.race_x, self.race_y)
	
	def next_race(self, race_sprite):
		print "Next race"
		self.race_index = (self.race_index + 1) % len(self.races)
		self.current_race = self.races[self.race_index]

		self.race_sprite_path = RACE_SPRITES[self.current_race]
		print self.race_index, self.current_race, self.race_sprite_path
		self.race = race_tile(self.current_race)
		self.race_sprite = self.race.get_sprite(self.race_x, self.race_y)

	def prev_class(self, *param):
		print "Previous class"
	
	def next_class(self, *param):
		print "Next class"

	def char_add(self, character):
		try:
			print "Added character to team"
			self.party.remove(character)
			self.team.append(character)
			self.update_char_panels()
		except ValueError:
			self.char_rm(character)

	def char_rm(self, character):
		print "Removed character from team"
		self.team.remove(character)
		self.party.append(character)
		self.update_char_panels()

	def char_manage(self, character):
		print "Selected character for managing"
		self.selected_char = character
		self.update_char_panels()

	def enable_buttons(self, i):
		for b in range(1, len(self.parent_buttons[i])):
			self.parent_buttons[i][b].toggle_visibility()
	
	def click(self, event, container):
		for b in self.manager_buttons:
			if b.contains(*event.pos):
				f = b.function[0]
				f(b.function[1])
		for b in container.children:
			if b.parent_button.contains(*event.pos):
				b.parent_button.toggle()
				b.enable_buttons()
				break
			else:
				for c in b.child_buttons:
					if c.contains(*event.pos):
						f = c.function[0]
						f(c.function[1])

	def loop(self):
		while 1:
			self.screen.fill((127, 127, 127))
			self.manage.draw()
			self.party_con.draw()
			self.inventory.draw()
			self.team_con.draw()
			self.char_inventory.draw()
			pygame.display.flip()

			for event in pygame.event.get():
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						self.click(event, self.inventory)
						self.click(event, self.party_con)
						self.click(event, self.manage)
						self.click(event, self.team_con)
						self.click(event, self.char_inventory)
				elif event.type == pygame.QUIT:
					sys.exit()

			time.sleep(0.05)

if __name__ == "__main__":
	win = UItest()
	win.loop()
