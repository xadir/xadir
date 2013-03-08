import sys, time
import pygame
import string
from resources import *
from UI import *
from character import Character
from charsprite import CharacterSprite
from race import races
from charclass import classes
from store import *
from game import start_game, host_game, join_game
from weapon import Weapon, weapons
from armor import Armor, armors
from player import Player
from selectdialog import TextList
from wire import serialize, deserialize
import random
import eztext

from mapselection import MapSelection
from resolver import *

import asyncore
import asynchat
import socket
import server
from server import CentralConnectionBase

DEFAULT_CENTRAL_HOST = 'gameserver.xadir.net'

if not pygame.font:
	print "Warning: Fonts not enabled"
if not pygame.mixer:
	print "Warning: Audio not enabled"

class FakeGrid:
	def __init__(self, size):
		self.x, self.y = (0, 0)
		self.cell_size = size

class NameList(TextList):
	def format_item(self, item):
		return item.name

class Server:
	def __init__(self, ip, ping, players):
		self.ip = ip
		self.ping = ping
		self.playerlist = players

class Challenge:
	def __init__(self, players, map):
		self.players = players
		self.map = map

class NetworkPlayer:
	def __init__(self, client_id, ip_addr, nicks):
		self.client_id = client_id
		self.ip_addr = ip_addr
		self.nicks = nicks
		self.name = '%s (%d)' % (nicks[0] if nicks else '?', len(nicks))

class LoungeConnection(CentralConnectionBase):
	def __init__(self, manage, host, port):
		CentralConnectionBase.__init__(self, socket.socket())

		self.manage = manage
		self.nicks = [player.name for player in manage.players]
		self.client_id = None
		self.users = {}

		self.connect((host, port))

	def handle_version(self, cmd, args):
		CentralConnectionBase.handle_version(self, cmd, args)
		self.push_cmd('NICK', serialize(self.nicks, 'list', 'unicode'))
		self.handler = self.handle_id

	def handle_id(self, cmd, args):
		assert cmd == 'ID'
		self.client_id = deserialize(args, 'int')
		self.handler = self.handle_nicks

	def handle_nicks(self, cmd, args):
		assert cmd == 'NICKS'
		users = deserialize(args, 'list', 'tuple', ['int', 'str', ['list', 'unicode']])
		for client_id, ip_addr, nicks in users:
			player = NetworkPlayer(client_id, ip_addr, nicks)
			self.users[client_id] = player
			self.manage.networkplayers.append(player)
		self.handler = self.handle_general

	def handle_general(self, cmd, args):
		if cmd == 'MSG':
			client_id, msg = deserialize(args, 'tuple', ['int', 'unicode'])
			self.manage.network_messages.items.append('%s: %s' % (self.users[client_id].name, msg))
		elif cmd == 'JOIN':
			client_id, ip_addr, nicks = deserialize(args, 'tuple', ['int', 'str', ['list', 'unicode']])
			player = NetworkPlayer(client_id, ip_addr, nicks)
			self.users[client_id] = player
			self.manage.networkplayers.append(player)
		elif cmd == 'QUIT':
			client_id = deserialize(args, 'int')
			del self.users[client_id]
			# XXX: ugh...
			self.manage.networkplayers[:] = [player for player in self.manage.networkplayers if player.client_id != client_id]
		else:
			self.die('Unknown command: ' + repr(cmd))

	def send_message(self, msg):
		self.push_cmd('MSG', serialize(msg, 'unicode'))

	def handle_close(self):
		self.manage.handle_disconnect()
		self.close()

class Manager:
	def __init__(self, screen):

		### Objects to implement multi-round game

		self.saved_players = []
		self.players = []
		self.player = None

		self.server = Server("0.0.0.0", 23, [Player("test1", [], [], 100), Player("test2", [], [], 100), Player("test3", [], [], 100), Player("test4", [], [], 100)])

		self.networkplayers = []
		self.selected_networkplayers = []
		self.received_challenges = []
		self.received_challenges.append(Challenge([Player("test1", [], [], 100), Player("test2", [], [], 100)], "new_map.txt"))

#		self.selected_networkplayers.append(self.server.playerlist[0])

		self.screen = screen
		self.sword_icon = pygame.image.load(os.path.join(GFXDIR, "weapon_icon.png"))
#		self.armor_icon = pygame.image.load(os.path.join(GFXDIR, "armor_icon.png"))

		self.res = Resources(None)

		self.ip = ''
		IpResolver('manager', self).start()

		self.team = []

#		self.inventory = self.player.inventory
#		self.char_inventory = []

		self.selected_char = None
		self.selected_item = None

		self.store = Store(10, 3000)

		self.local_con = UIContainer(None, (20, 20), (270, 200), self.screen)
		self.network_con = UIContainer(None, (20, 230), (270, 430), self.screen)
		self.manage = UIContainer(None, (320, 20), (300, 250), self.screen)
		self.party_con = UIContainer(None, (710, 20), (152, 250), self.screen)
		self.inventory_con = UIContainer(None, (710, 290), (152, 380), self.screen)
		self.char_inventory_con = UIContainer(None, (540, 20), (152, 250), self.screen)
		self.team_con = UIContainer(None, (320, 290), (371, 120), self.screen)
		self.store_con = UIContainer(None, (880, 120), (298, 550), self.screen)
		self.item_con = UIContainer(None, (320, 450), (371, 220), self.screen)
		self.text_con = UIContainer(None, (880, 20), (298, 80), self.screen)
		self.textfield_con = UIContainer(None, (20, 20), (600, 430), self.screen)

		self.saved_playerlist = NameList(self.local_con, (10, 90), (100, 100), self.saved_players, selected = self.select_saved_player, multi = True)
		self.local_playerlist = NameList(self.local_con, (120, 90), (100, 100), self.players, selected = self.select_player)
		self.network_playerlist_all = None
		self.network_playerlist_selected = None
		self.network_messages = None

		self.sprites = pygame.sprite.LayeredUpdates()
		self.sprites.add(self.local_playerlist)
		self.sprites.add(self.saved_playerlist)

		self.race_sprite_x = self.manage.x + 90
		self.race_sprite_y = self.manage.y + 20
		self.manager_buttons = []
		self.new_char_buttons = []
		self.manager_char_buttons = []
		self.manager_texts = []
		self.local_con_buttons = []
		self.network_buttons = []
		self.network_playerlist_buttons = []

		self.network_play_btn = FuncButton(self.network_con, 10, 100, 70, 30, [["Play", None]], None, ICON_FONTSIZE, self.screen, 1, (self.start_hotseat_game, None), True, False, True)
		self.network_connect_btn = FuncButton(self.network_con, 10, 140, 70, 30, [["Connect", None]], None, ICON_FONTSIZE, self.screen, 1, (self.connect_server, None), True, False, True)
		self.network_host_btn = FuncButton(self.network_con, 10, 180, 70, 30, [["Host", None]], None, ICON_FONTSIZE, self.screen, 1, (self.host_server, None), True, False, True)
		self.network_disconnect_btn = FuncButton(self.network_con, 10, 390, 70, 30, [["Disconnect", None]], None, ICON_FONTSIZE, self.screen, 1, (self.disconnect_server, None), True, False, True)
		self.network_ready_btn = FuncButton(self.network_con, 90, 390, 70, 30, [["Ready", None]], None, ICON_FONTSIZE, self.screen, 1, (self.ready_server, None), True, False, True)
		self.network_challenge_btn = FuncButton(self.network_con, 170, 390, 70, 30, [["Challenge", None]], None, ICON_FONTSIZE, self.screen, 1, (self.send_challenge, None), True, False, True)

		self.ezfont = pygame.font.Font(FONT, int(24*FONTSCALE))

		self.player_input = eztext.Input(self.local_con, (10, 10), (250, 25), maxlength=15, color=COLOR_FONT, prompt='Player name: ', font = self.ezfont)

		self.ip_input = eztext.Input(self.network_con, (10, 10), (250, 25), maxlength=20, color=COLOR_FONT, prompt='IP: ', font = self.ezfont)
		self.port_input = eztext.Input(self.network_con, (10, 45), (250, 25), maxlength=5, restricted='0123456789', color=COLOR_FONT, prompt='Port: ', font = self.ezfont)

		self.ip_input.value = DEFAULT_CENTRAL_HOST
		self.port_input.value = "33333"

		self.message_input = eztext.Input(self.network_con, (10, 370), (250, 16), maxlength=25, color=COLOR_FONT, prompt='Message: ', font = pygame.font.Font(FONT, int(16*FONTSCALE)), handle_enter = self.send_message)

		self.sprites.add([self.player_input, self.ip_input, self.port_input, self.message_input])

		self.connect_buttons = []
		self.connect_buttons.append(self.network_play_btn)
		self.connect_buttons.append(self.network_connect_btn)
		self.connect_buttons.append(self.network_host_btn)
		self.save_btn = FuncButton(self.manage, 10, 210, 100, 30, [["Save", None]], None, ICON_FONTSIZE, self.screen, 1, (self.new_char, self.selected_char), True, False, True)
		self.play_btn = FuncButton(self.team_con, 10, 80, 70, 30, [["Play", None]], None, ICON_FONTSIZE, self.screen, 1, (self.start_game, self.team), True, False, True)
		self.join_btn = FuncButton(self.team_con, 85, 80, 70, 30, [["Join", None]], None, ICON_FONTSIZE, self.screen, 1, (self.join_game, self.team), True, False, True)
		self.host_btn = FuncButton(self.team_con, 160, 80, 70, 30, [["Host", None]], None, ICON_FONTSIZE, self.screen, 1, (self.host_game, self.team), True, False, True)		
		self.save_player_btn = FuncButton(self.team_con, 260, 80, 100, 30, [["Save player", None]], None, ICON_FONTSIZE, self.screen, 1, (self.save_selected_player, None), True, False, True)
		self.new_char_btn = FuncButton(self.party_con, 10, 210, 130, 30, [["New", None]], None, ICON_FONTSIZE, self.screen, 1, (self.new_character, self.manage), True, False, True)

		self.manager_buttons.append(self.save_btn)
		self.manager_buttons.append(self.play_btn)
		self.manager_buttons.append(self.join_btn)
		self.manager_buttons.append(self.host_btn)
		self.manager_buttons.append(self.save_player_btn)
		self.manager_buttons.append(self.new_char_btn)

		self.addplayer_btn = FuncButton(self.local_con, 10, 50, 200, 30, [["Add player", None]], None, ICON_FONTSIZE, self.screen, 1, (self.add_player, None), True, False, True)

		self.local_con_buttons.append(self.addplayer_btn)

		self.local_con.spritegroup.add(self.addplayer_btn)

#		self.update_char_panels()
		self.update_store()
#		self.update_general_texts()
		self.show_connect_panel()

		self.network_connected = False
		self.update_text_fields()

		self.load_all_players()

	def send_message(self):
		self.lounge.send_message(self.message_input.value)
		self.message_input.value = ''

	def load_all_players(self):
		for fname in os.listdir(SAVEDIR):
			if not fname.endswith('.sav'):
				continue
			self.load_and_add_player(fname)

	def load_and_add_player(self, fname):
		with file(os.path.join(SAVEDIR, fname), 'rb') as f:
			data = f.read()

		player = deserialize(data, 'Player')
		self.saved_players.append(player)

	def save_player(self, player):
		fname = player.name + '.sav'
		data = serialize(player, 'Player')

		with file(os.path.join(SAVEDIR, fname), 'wb') as f:
			f.write(data)

	def save_selected_player(self, xxx):
		self.save_player(self.player)

	def update_general_texts(self):

		self.text_con.clear()

		texts = pygame.Surface((200,60))
		texts.fill(COLOR_BG)
		text_y = 0
		
		font = pygame.font.Font(FONT, int(20*FONTSCALE))
		text = font.render("Player: " + str(self.player.money) + "c", True, COLOR_FONT, COLOR_BG)
		rect = text.get_rect()
		rect.x = 0
		rect.y = text_y
		texts.blit(text, rect)
		text_y += 15

		font = pygame.font.Font(FONT, int(20*FONTSCALE))
		text = font.render("Store: " + str(self.store.money) + "c", True, COLOR_FONT, COLOR_BG)
		rect = text.get_rect()
		rect.x = 0
		rect.y = text_y
		texts.blit(text, rect)
		text_y += 15

		if self.selected_item != None:
			font = pygame.font.Font(FONT, int(20*FONTSCALE))
			text = font.render("Selected item: " + str(self.selected_item), True, COLOR_FONT, COLOR_BG)
			rect = text.get_rect()
			rect.x = 0
			rect.y = text_y
			texts.blit(text, rect)
			text_y += 15

		text_sprite = pygame.sprite.Sprite()
		text_sprite.image = texts
		rect = texts.get_rect()
		rect.x = self.text_con.x + 10
		rect.y = self.text_con.y + 10
		text_sprite.rect = rect
		print texts, texts.get_rect()
		self.text_con.spritegroup.add(text_sprite)

	def update_text_fields(self):
		if not self.network_connected:
			self.sprites.add([self.ip_input, self.port_input])
			self.sprites.remove(self.message_input)
		else:
			self.sprites.remove([self.ip_input, self.port_input])
			self.sprites.add(self.message_input)

	def update_inventories(self):
		print self.inventory, self.char_inventory
		self.inventory_con.clear()
		for item in self.inventory:
			self.add_auto_item('player', self.inventory_con, item)

		self.char_inventory_con.clear()
		for item in self.char_inventory:
			self.add_auto_item('char', self.char_inventory_con, item)

	def update_store(self):
		print "Store inventory: ", self.store.items, "Store balance: ", self.store.money
		self.store_con.clear()
		for item in self.store.items:
			self.add_auto_item('store', self.store_con, item)

	def add_auto_item(self, container_type, container, item):
		if isinstance(item, Weapon):
			self.add_item(self.sword_icon, item.name.capitalize(), container, item, container_type)
		elif isinstance(item, Armor):
			armor_icon = self.res.armors[item.style]['human'][270]
			self.add_item(armor_icon, item.name.capitalize(), container, item, container_type)

	def show_connect_panel(self):
		print "Showing connecting panel"
		self.network_buttons = []
		self.network_con.clear()
		self.network_con.spritegroup.add(self.network_play_btn)
		self.network_buttons.append(self.network_play_btn)
		self.network_con.spritegroup.add(self.network_connect_btn)
		self.network_buttons.append(self.network_connect_btn)
		self.network_con.spritegroup.add(self.network_host_btn)
		self.network_buttons.append(self.host_btn)

	def show_network_panel(self):
		self.network_con.clear()
		
		texts = pygame.Surface((260,65))
		texts.fill(COLOR_BG)
		text_x = 0
		
		font = pygame.font.Font(FONT, int(30*FONTSCALE))
		text = font.render("IP: " + "0.0.0.0", True, COLOR_FONT, COLOR_BG)
		rect = text.get_rect()
		rect.x = text_x
		rect.y = 0
		texts.blit(text, rect)
		text_x += 100

		font = pygame.font.Font(FONT, int(30*FONTSCALE))
		text = font.render("Ping: " + str(9999) + "ms", True, COLOR_FONT, COLOR_BG)
		rect = text.get_rect()
		rect.x = text_x
		rect.y = 0
		texts.blit(text, rect)

		font = pygame.font.Font(FONT, int(25*FONTSCALE))
		text = font.render("Players", True, COLOR_FONT, COLOR_BG)
		rect = text.get_rect()
		rect.x = 0
		rect.y = 40
		texts.blit(text, rect)

		font = pygame.font.Font(FONT, int(25*FONTSCALE))
		text = font.render("Challenges", True, COLOR_FONT, COLOR_BG)
		rect = text.get_rect()
		rect.x = 0
		rect.y = 190
		texts.blit(text, rect)

		text_sprite = pygame.sprite.Sprite()
		text_sprite.image = texts
		rect = texts.get_rect()
		rect.x = self.network_con.x + 10
		rect.y = self.network_con.y + 10
		text_sprite.rect = rect
		self.network_con.spritegroup.add(text_sprite)

		self.network_buttons = []
		self.network_con.spritegroup.add(self.network_disconnect_btn)
		self.network_con.spritegroup.add(self.network_ready_btn)
		self.network_con.spritegroup.add(self.network_challenge_btn)
		self.network_buttons.append(self.network_challenge_btn)
		self.network_buttons.append(self.network_disconnect_btn)
		self.network_buttons.append(self.network_ready_btn)
		if len(self.selected_networkplayers) > 0:
			self.network_buttons.append(self.network_challenge_btn)

		#self.update_challengelist()

	def update_network_panel(self):
		self.show_network_panel()
		self.network_con.draw(True)

	def update_challengelist(self):
		print "Updating received challenges"
		self.network_challengelist_buttons = []
		btn_y = 0
		for c in self.received_challenges:
			btn = FuncButton(self.network_con, self.network_con.x + 10, self.network_con.y + btn_y, 200, 20, [[c.players[0].name + " (" +  str(len(c.players)) + ")", None]], None, ICON_FONTSIZE, self.screen, 1, None, True, False, True)
			btn.function = (self.accept_challenge, c)
			btn_y += 30
			self.network_con.spritegroup.add(btn)
			self.network_challengelist_buttons.append(btn)

	def update_server_chat(self):
		print "Updating server chat"

	def update_char_panels(self):
		self.party_con.clear()
		for char in self.party:
			self.add_char(char.race.name, self.party_con, char, False)

		self.team_con.clear()
		for char in self.team:
			self.add_char(char.race.name, self.team_con, char, True)

		self.manage.clear()

		#self.manage.spritegroup.add(self.save_btn)
		self.team_con.spritegroup.add(self.save_player_btn)
		self.party_con.spritegroup.add(self.new_char_btn)

		self.manager_texts = []
		self.manager_char_buttons = []
		#int self.selected_char
		if self.selected_char != None:
			self.char_new = False
			
			self.selected_charsprite = CharacterSprite(None, self.selected_char, (0,0), 270, FakeGrid(CHAR_SIZE), self.res)
			
			self.selected_charsprite.x = self.race_sprite_x
			self.selected_charsprite.y = self.race_sprite_y + 8 #XXX hack

			self.race_sprite = self.selected_charsprite
			self.manage.spritegroup.add(self.race_sprite)

			self.char_inventory = [self.selected_char.weapon, self.selected_char.armor]
			self.update_inventories()

			# Get printable variables of the selected character: name, race_name, class_name, str, dex, con, int
			print self.selected_char.name, self.selected_char.race.name, self.selected_char.class_
			print "Str: " + str(self.selected_char.str), "Dex: " + str(self.selected_char.dex)
			print  "Con: " + str(self.selected_char.con), "Int: " + str(self.selected_char.int)

			texts = pygame.Surface((140,150))
			texts.fill(COLOR_BG)
			text_y = 0

			font = pygame.font.Font(FONT, int(20*FONTSCALE))
			text = font.render(string.capitalize(self.selected_char.name), True, COLOR_FONT, COLOR_BG)
			rect = text.get_rect()
			rect.centerx = 70
			rect.y = text_y
			texts.blit(text, rect)
			text_y += 15

			text = font.render(string.capitalize(self.selected_char.race.name), True, COLOR_FONT, COLOR_BG)
			rect = text.get_rect()
			rect.centerx = 70
			rect.y = text_y
			texts.blit(text, rect)
			text_y += 15

			if self.selected_char.class_ != None:
				text = font.render(string.capitalize(self.selected_char.class_.name), True, COLOR_FONT, COLOR_BG)
				rect = text.get_rect()
				rect.centerx = 70
				rect.y = text_y
				texts.blit(text, rect)
				text_y += 15

			text = font.render("Str: " + str(self.selected_char.str), True, COLOR_FONT, COLOR_BG)
			rect = text.get_rect()
			rect.left = 0
			rect.y = text_y
			texts.blit(text, rect)

			text = font.render("Dex: " + str(self.selected_char.dex), True, COLOR_FONT, COLOR_BG)
			rect = text.get_rect()
			rect.left = 80
			rect.y = text_y
			texts.blit(text, rect)
			text_y += 30

			text = font.render("Con: " + str(self.selected_char.con), True, COLOR_FONT, COLOR_BG)
			rect = text.get_rect()
			rect.left = 0
			rect.y = text_y
			texts.blit(text, rect)

			text = font.render("Int: " + str(self.selected_char.int), True, COLOR_FONT, COLOR_BG)
			rect = text.get_rect()
			rect.left = 80
			rect.y = text_y
			texts.blit(text, rect)
			text_y += 25

			text = font.render("XP: " + str(self.selected_char.xp), True, COLOR_FONT, COLOR_BG)
			rect = text.get_rect()
			rect.left = 0
			rect.y = text_y
			texts.blit(text, rect)

			text = font.render("Level: " + str(self.selected_char.level), True, COLOR_FONT, COLOR_BG)
			rect = text.get_rect()
			rect.left = 80
			rect.y = text_y
			texts.blit(text, rect)
			text_y += 25

			if self.selected_char.upgrade_points > 0:
				text = font.render("Points left: " + str(self.selected_char.upgrade_points), True, COLOR_FONT, COLOR_BG)
				rect = text.get_rect()
				rect.left = 0
				rect.y = text_y
				texts.blit(text, rect)

			text_sprite = pygame.sprite.Sprite()
			text_sprite.image = texts
			rect = texts.get_rect()
			rect.centerx = self.race_sprite_x + 24
			rect.y = self.race_sprite_y + 70
			text_sprite.rect = rect
			print texts, texts.get_rect()
			self.manage.spritegroup.add(text_sprite)

			if self.selected_char.upgrade_points > 0:
				self.inc_str = FuncButton(self.manage, 15, 130, 20, 20, [["+", None]], None, ICON_FONTSIZE, self.screen, 1, (self.increase_str, self.selected_char), True, False, True)
				self.inc_dex = FuncButton(self.manage, 180, 130, 20, 20, [["+", None]], None, ICON_FONTSIZE, self.screen, 1, (self.increase_dex, self.selected_char), True, False, True)
				self.inc_con = FuncButton(self.manage, 15, 160, 20, 20, [["+", None]], None, ICON_FONTSIZE, self.screen, 1, (self.increase_con, self.selected_char), True, False, True)
				self.inc_int = FuncButton(self.manage, 180, 160, 20, 20, [["+", None]], None, ICON_FONTSIZE, self.screen, 1, (self.increase_int, self.selected_char), True, False, True)

				self.manager_char_buttons.append(self.inc_str)
				self.manage.spritegroup.add(self.inc_str)
				self.manager_char_buttons.append(self.inc_dex)
				self.manage.spritegroup.add(self.inc_dex)
				self.manager_char_buttons.append(self.inc_con)
				self.manage.spritegroup.add(self.inc_con)
				self.manager_char_buttons.append(self.inc_int)
				self.manage.spritegroup.add(self.inc_int)

	def update_item_panel(self):
		self.item_con.clear()
		
		if self.selected_item != None:

			texts = pygame.Surface((360,200))
			texts.fill(COLOR_BG)
			text_y = 0

			if isinstance(self.selected_item, Weapon):
				# Get printable variables of the selected weapon
				print "Weapon name: ", self.selected_item.name, " size: ", self.selected_item.size, " type: ", self.selected_item.type
				print "class: ", self.selected_item.class_, "damage: ", self.selected_item.damage, "damage_type: ", self.selected_item.damage_type
				print "Magic encharment", self.selected_item.magic_enchantment, "Critical multiplier", self.selected_item.critical_multiplier
				print "Critical chance", self.selected_item.critical_chance, "Price", self.selected_item.price


				font = pygame.font.Font(FONT, int(20*FONTSCALE))
				text = font.render(string.capitalize(self.selected_item.name), True, COLOR_FONT, COLOR_BG)
				rect = text.get_rect()
				rect.left = 0
				rect.y = text_y
				texts.blit(text, rect)
				text_y += 30

				text = font.render("Size: " + string.capitalize(self.selected_item.size), True, COLOR_FONT, COLOR_BG)
				rect = text.get_rect()
				rect.left = 0
				rect.y = text_y
				texts.blit(text, rect)

				text = font.render("Type: " + string.capitalize(self.selected_item.type), True, COLOR_FONT, COLOR_BG)
				rect = text.get_rect()
				rect.left = 120
				rect.y = text_y
				texts.blit(text, rect)
				text_y += 15

#				text = font.render("Class: " + string.capitalize(self.selected_item.class_), True, COLOR_FONT, COLOR_BG)
#				rect = text.get_rect()
#				rect.left = 80
#				rect.y = text_y
#				texts.blit(text, rect)
#				text_y += 15

				text = font.render("Damage: " + str(self.selected_item.damage), True, COLOR_FONT, COLOR_BG)
				rect = text.get_rect()
				rect.left = 0
				rect.y = text_y
				texts.blit(text, rect)

				for t in self.selected_item.damage_type:
					text = font.render("Damage type: " + str(t), True, COLOR_FONT, COLOR_BG)
					rect = text.get_rect()
					rect.left = 120
					rect.y = text_y
					texts.blit(text, rect)
					text_y += 16

				text_y += 10

				text = font.render("Magic enchantment: " + str(self.selected_item.magic_enchantment), True, COLOR_FONT, COLOR_BG)
				rect = text.get_rect()
				rect.left = 0
				rect.y = text_y
				texts.blit(text, rect)
				text_y += 15

				text = font.render("Critical multiplier: " + str(self.selected_item.critical_multiplier), True, COLOR_FONT, COLOR_BG)
				rect = text.get_rect()
				rect.left = 0
				rect.y = text_y
				texts.blit(text, rect)
				text_y += 15

				text = font.render("Critical chance: " + str(self.selected_item.critical_chance), True, COLOR_FONT, COLOR_BG)
				rect = text.get_rect()
				rect.left = 0
				rect.y = text_y
				texts.blit(text, rect)
				text_y += 15

				text = font.render("Price: " + str(self.selected_item.price), True, COLOR_FONT, COLOR_BG)
				rect = text.get_rect()
				rect.left = 0
				rect.y = text_y
				texts.blit(text, rect)
				text_y += 15


			if isinstance(self.selected_item, Armor):
				# Get printable variables of the selected weapon
				print "Armor name: ", self.selected_item.name, " miss chance: ", str(self.selected_item.miss_chance), " damage reduction: ", self.selected_item.damage_reduction
				print "enchanted damage reduction: ", self.selected_item.enchanted_damage_reduction, "enchantd damage reduction type: ", self.selected_item.enchanted_damage_reduction_type
				print "Price", self.selected_item.price, "style", self.selected_item.style

				font = pygame.font.Font(FONT, int(20*FONTSCALE))
				text = font.render(string.capitalize(self.selected_item.name), True, COLOR_FONT, COLOR_BG)
				rect = text.get_rect()
				rect.left = 0
				rect.y = text_y
				texts.blit(text, rect)
				text_y += 30

				text = font.render("Style: " + string.capitalize(self.selected_item.style), True, COLOR_FONT, COLOR_BG)
				rect = text.get_rect()
				rect.left = 0
				rect.y = text_y
				texts.blit(text, rect)
				text_y += 15

				text = font.render("Miss chance: " + string.capitalize(str(self.selected_item.miss_chance)), True, COLOR_FONT, COLOR_BG)
				rect = text.get_rect()
				rect.left = 0
				rect.y = text_y
				texts.blit(text, rect)
				text_y += 0

				text = font.render("Damage reduction: " + string.capitalize(str(self.selected_item.damage_reduction)), True, COLOR_FONT, COLOR_BG)
				rect = text.get_rect()
				rect.left = 120
				rect.y = text_y
				texts.blit(text, rect)
				text_y += 25

				text = font.render("Enchanted damage reduction: " + string.capitalize(str(self.selected_item.enchanted_damage_reduction)), True, COLOR_FONT, COLOR_BG)
				rect = text.get_rect()
				rect.left = 0
				rect.y = text_y
				texts.blit(text, rect)
				text_y += 15

				text = font.render("Enchanted damage reduction type: " + string.capitalize(str(self.selected_item.enchanted_damage_reduction_type)), True, COLOR_FONT, COLOR_BG)
				rect = text.get_rect()
				rect.left = 0
				rect.y = text_y
				texts.blit(text, rect)
				text_y += 15

				text = font.render("Price: " + string.capitalize(str(self.selected_item.price)), True, COLOR_FONT, COLOR_BG)
				rect = text.get_rect()
				rect.left = 0
				rect.y = text_y
				texts.blit(text, rect)
				text_y += 15


			text_sprite = pygame.sprite.Sprite()
			text_sprite.image = texts
			rect = texts.get_rect()
			rect.left = self.item_con.x + 10
			rect.top = self.item_con.y + 10
			text_sprite.rect = rect
			print texts, texts.get_rect()
			self.item_con.spritegroup.add(text_sprite)

	def add_char(self, race, container, character, in_team=False):
		charsprite = CharacterSprite(None, character, (0,0), 270, FakeGrid(CHAR_SIZE), self.res)
		charsprite.update()
		race_image = charsprite.image
		
		cropped = pygame.Surface((36, 40))
		cropped.fill(COLOR_BG)
		cropped.blit(race_image, (0, 0), (6, 12, 36, 40))

		icon_rect = cropped.get_rect()
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
		
		tmp = CascadeButton(container, self.screen, x, y, img_width + (ICON_PADDING * 2), img_height + (ICON_PADDING * 2), None, [[cropped, None]])
		tmp.add_button((0, img_height + (ICON_PADDING * 2)), (img_width+ (ICON_PADDING * 2), 30), [["Manage", None]], None, (self.char_manage, character), False, False, None)
		if in_team:
			tmp.add_button((0, -32), (img_width+ (ICON_PADDING * 2), 30), [["Deselect", None]], None, (self.char_add, character), False, False, None)
		else:
			tmp.add_button((0, -32), (img_width+ (ICON_PADDING * 2), 30), [["Select", None]], None, (self.char_add, character), False, False, None)
		container.children.append(tmp)

	def add_item(self, icon, text, container, item=None, inventory_type=None):
		img_width = 134
		img_height = 40
		icon_width = (ICON_BORDER + ICON_PADDING + img_width + ICON_PADDING + ICON_BORDER) # To clarify to layout
		icon_height = (ICON_BORDER + ICON_PADDING + img_height + ICON_PADDING + ICON_BORDER)
		icon_num = len(container.children)
		icon_place = [0,0]
		icon_place[0] = (icon_num % (container.width / icon_width))
		icon_place[1] = (icon_num / (container.width / icon_width))
		x = (ICON_MARGIN * 2) + (icon_place[0] * (ICON_MARGIN + icon_width))
		y = (ICON_MARGIN * 2) + (icon_place[1] * (ICON_MARGIN + icon_height))
		
		tmp = CascadeButton(container, self.screen, x, y, img_width + (ICON_PADDING * 2), img_height + (ICON_PADDING * 2), [[text, None]], [[icon, (2, 2)]], None, [self.inspect_item, item])
		if inventory_type == "char":
			tmp.add_button((0, img_height + (ICON_PADDING * 2)), (img_width+ (ICON_PADDING * 2), 30), [["Sell", None]], None, (self.sell, [item, self.char_inventory]), False, False, None)
			tmp.add_button((0, -32), (img_width+ (ICON_PADDING * 2), 30), [["Yield", None]], None, (self.unequip, item), False, False, None)
		elif inventory_type == "player":
			tmp.add_button((0, img_height + (ICON_PADDING * 2)), (img_width+ (ICON_PADDING * 2), 30), [["Sell", None]], None, (self.sell, [item, self.inventory]), False, False, None)
			tmp.add_button((0, -32), (img_width+ (ICON_PADDING * 2), 30), [["Equip", None]], None, (self.equip, item), False, False, None)
		elif inventory_type == "store":
			tmp.add_button((0, img_height + (ICON_PADDING * 2)), (img_width+ (ICON_PADDING * 2), 30), [["Buy", None]], None, (self.buy, item), False, False, None)
		container.children.append(tmp)

	def new_character(self, container):
		self.char_new = True
		for b in self.new_char_buttons:
			print b.function

		self.manage.clear()
		self.char_inventory_con.clear()
		self.new_char_buttons = []

		self.manage.spritegroup.add(self.save_btn)
		self.team_con.spritegroup.add(self.play_btn)
		self.team_con.spritegroup.add(self.join_btn)
		self.team_con.spritegroup.add(self.host_btn)
		self.party_con.spritegroup.add(self.new_char_btn)

		self.race_index = 0
		self.class_index = 0
		self.hair_index = 0

		self.classes = ['warrior', 'wizard', 'rogue']

		self.races = self.res.races.keys()
		self.hairs = self.res.hairs.keys()

		self.current_race = self.races[self.race_index]
		self.current_class = self.classes[self.class_index]
		self.current_hair = self.hairs[self.hair_index]
		print self.current_class
		self.selected_char = Character("test", self.current_race, self.current_class, 0, 0, 0, 0, 0, None, None)
		self.selected_charsprite = CharacterSprite(None, self.selected_char, (0,0), 270, FakeGrid(CHAR_SIZE), self.res)

		self.selected_charsprite.x = self.race_sprite_x
		self.selected_charsprite.y = self.race_sprite_y + 8 #XXX hack

		self.race_sprite = self.selected_charsprite
		container.spritegroup.add(self.race_sprite)

		self.prev_hair_btn = FuncButton(self.manage, 50, 20, 20, 20, [["<", None]], None, ICON_FONTSIZE, self.screen, 1, (self.prev_hair, self.selected_char), True, False, True)
		self.next_hair_btn = FuncButton(self.manage, 155, 20, 20, 20, [[">", None]], None, ICON_FONTSIZE, self.screen, 1, (self.next_hair, self.selected_char), True, False, True)

		self.new_char_buttons.append(self.prev_hair_btn)
		container.spritegroup.add(self.prev_hair_btn)
		self.new_char_buttons.append(self.next_hair_btn)
		container.spritegroup.add(self.next_hair_btn)

		self.prev_char = FuncButton(self.manage, 50, 55, 20, 20, [["<", None]], None, ICON_FONTSIZE, self.screen, 1, (self.prev_race, self.race_sprite), True, False, True)
		self.next_char = FuncButton(self.manage, 155, 55, 20, 20, [[">", None]], None, ICON_FONTSIZE, self.screen, 1, (self.next_race, self.race_sprite), True, False, True)

		self.new_char_buttons.append(self.prev_char)
		container.spritegroup.add(self.prev_char)
		self.new_char_buttons.append(self.next_char)
		container.spritegroup.add(self.next_char)

		self.prev_class_ = FuncButton(self.manage, 50, 105, 20, 20, [["<", None]], None, ICON_FONTSIZE, self.screen, 1, (self.prev_class, self.selected_char), True, False, True)
		self.next_class_ = FuncButton(self.manage, 155, 105, 20, 20, [[">", None]], None, ICON_FONTSIZE, self.screen, 1, (self.next_class, self.selected_char), True, False, True)

		self.new_char_buttons.append(self.prev_class_)
		container.spritegroup.add(self.prev_class_)
		self.new_char_buttons.append(self.next_class_)
		container.spritegroup.add(self.next_class_)
		

		self.inc_str = FuncButton(self.manage, 15, 135, 20, 20, [["+", None]], None, ICON_FONTSIZE, self.screen, 1, (self.increase_str, self.selected_char), True, False, True)
		self.inc_dex = FuncButton(self.manage, 180, 135, 20, 20, [["+", None]], None, ICON_FONTSIZE, self.screen, 1, (self.increase_dex, self.selected_char), True, False, True)
		self.inc_con = FuncButton(self.manage, 15, 166, 20, 20, [["+", None]], None, ICON_FONTSIZE, self.screen, 1, (self.increase_con, self.selected_char), True, False, True)
		self.inc_int = FuncButton(self.manage, 180, 166, 20, 20, [["+", None]], None, ICON_FONTSIZE, self.screen, 1, (self.increase_int, self.selected_char), True, False, True)

		self.new_char_buttons.append(self.inc_str)
		container.spritegroup.add(self.inc_str)
		self.new_char_buttons.append(self.inc_dex)
		container.spritegroup.add(self.inc_dex)
		self.new_char_buttons.append(self.inc_con)
		container.spritegroup.add(self.inc_con)
		self.new_char_buttons.append(self.inc_int)
		container.spritegroup.add(self.inc_int)

		text_sprite = self.generate_char_text_sprite()
		self.manage.spritegroup.add(text_sprite)

	def update_new_character(self, container):
		print "Update", self.selected_char.class_

		container.clear()

		self.selected_charsprite.x = self.race_sprite_x
		self.selected_charsprite.y = self.race_sprite_y + 8 #XXX hack

		self.race_sprite = self.selected_charsprite
		container.spritegroup.add(self.race_sprite)
		self.manage.spritegroup.add(self.save_btn)

		container.spritegroup.add(self.prev_hair_btn)
		container.spritegroup.add(self.next_hair_btn)
		container.spritegroup.add(self.prev_char)
		container.spritegroup.add(self.next_char)
		container.spritegroup.add(self.prev_class_)
		container.spritegroup.add(self.next_class_)
		container.spritegroup.add(self.inc_str)
		container.spritegroup.add(self.inc_dex)
		container.spritegroup.add(self.inc_con)
		container.spritegroup.add(self.inc_int)

		text_sprite = self.generate_char_text_sprite()
		self.manage.spritegroup.add(text_sprite)

	def generate_char_text_sprite(self):
		texts = pygame.Surface((140,150))
		texts.fill(COLOR_BG)
		text_y = 0

		font = pygame.font.Font(FONT, int(20*FONTSCALE))
		text = font.render(string.capitalize(self.selected_char.race.name), True, COLOR_FONT, COLOR_BG)
		rect = text.get_rect()
		rect.centerx = 70
		rect.y = text_y
		texts.blit(text, rect)
		text_y += 20

		text = font.render(string.capitalize(self.selected_char.class_.name), True, COLOR_FONT, COLOR_BG)
		rect = text.get_rect()
		rect.centerx = 70
		rect.y = text_y
		texts.blit(text, rect)
		text_y += 30

		text = font.render("Str: " + str(self.selected_char.str), True, COLOR_FONT, COLOR_BG)
		rect = text.get_rect()
		rect.left = 0
		rect.y = text_y
		texts.blit(text, rect)

		text = font.render("Dex: " + str(self.selected_char.dex), True, COLOR_FONT, COLOR_BG)
		rect = text.get_rect()
		rect.left = 90
		rect.y = text_y
		texts.blit(text, rect)
		text_y += 30

		text = font.render("Con: " + str(self.selected_char.con), True, COLOR_FONT, COLOR_BG)
		rect = text.get_rect()
		rect.left = 0
		rect.y = text_y
		texts.blit(text, rect)

		text = font.render("Int: " + str(self.selected_char.int), True, COLOR_FONT, COLOR_BG)
		rect = text.get_rect()
		rect.left = 90
		rect.y = text_y
		texts.blit(text, rect)
		text_y += 25

		text = font.render(string.capitalize("Points left: "+ str(self.selected_char.upgrade_points)), True, COLOR_FONT, COLOR_BG)
		rect = text.get_rect()
		rect.centerx = 70
		rect.y = text_y
		texts.blit(text, rect)

		text_sprite = pygame.sprite.Sprite()
		text_sprite.image = texts
		rect = texts.get_rect()
		rect.centerx = self.race_sprite_x + 24
		rect.y = self.race_sprite_y + 70
		text_sprite.rect = rect

		return text_sprite

	def button_click(self):
		print "Clicked button"

	def sell(self, params):
		item = params[0]
		inventory = params[1]
		print "Item sold"
		if inventory == self.char_inventory:
			if self.selected_char.weapon == item:
				self.selected_char.weapon = None
			elif self.selected_char.armor == item:
				self.selected_char.armor = None
		inventory.remove(item)
		self.player.money += item.price
		self.store.sell_item_to_store(item)
		self.update_store()
		self.update_inventories()
		self.update_general_texts()

	def buy(self, item):
		if self.player.money >= item.price:
			self.inventory.append(item)
			self.player.money -= item.price
			self.store.buy_item_from_store(item)
			self.update_store()
			self.update_inventories()
			self.update_general_texts()

	def inspect_item(self, item):
		self.selected_item = item
		self.update_item_panel()

	def equip(self, item):
		print "Item equipped", item, self.selected_char
		if self.selected_char != None:
			if isinstance(item, Weapon):
				if self.selected_char.weapon == None:
					self.selected_char.weapon = item
					self.inventory.remove(item)
					self.char_inventory.append(item)
			elif isinstance(item, Armor):
				if self.selected_char.armor == None:
					self.selected_char.armor = item
					self.inventory.remove(item)
					self.char_inventory.append(item)
		self.update_inventories()

	def unequip(self, item):
		print "Item yielded", item, self.selected_char
		if self.selected_char != None:
			if isinstance(item, Weapon):
				self.selected_char.weapon = None
				self.char_inventory.remove(item)
				self.inventory.append(item)
			elif isinstance(item, Armor):
				self.selected_char.armor = None
				self.char_inventory.remove(item)
				self.inventory.append(item)
		self.update_inventories()

	def prev_hair(self, char):
		print "Previous hair"
		self.hair_index = (self.hair_index - 1) % len(self.hairs)
		self.selected_char.hair_name = self.hairs[self.hair_index]
		print self.selected_charsprite.hair_name
		self.selected_charsprite.update() #XXX hack
		self.update_new_character(self.manage)

	def next_hair(self, char):
		print "Next hair"
		self.hair_index = (self.hair_index + 1) % len(self.hairs)
		self.selected_char.hair_name = self.hairs[self.hair_index]
		self.selected_charsprite.update() #XXX hack
		self.update_new_character(self.manage)

	def prev_race(self, race_sprite):
		print "Previous race"
		print self.races
		self.race_index = (self.race_index - 1) % len(self.races)
		self.selected_char.race_name = races[self.races[self.race_index]].name
		self.update_new_character(self.manage)
	
	def next_race(self, race_sprite):
		print "Next race"
		self.race_index = (self.race_index + 1) % len(self.races)
		self.selected_char.race_name = races[self.races[self.race_index]].name
		self.update_new_character(self.manage)

	def prev_armour(self, char):
		print "Previous armour"
	
	def next_armour(self, char):
		print "Next armour"

	def prev_class(self, *param):
		print "Previous class"
		self.class_index = (self.class_index - 1) % len(self.classes)
		self.selected_char.class_name = classes[self.classes[self.class_index]].name
		self.update_new_character(self.manage)
	
	def next_class(self, *param):
		print "Next class"
		self.class_index = (self.class_index + 1) % len(self.classes)
		self.selected_char.class_name = classes[self.classes[self.class_index]].name
		self.update_new_character(self.manage)

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

	def new_char(self, character):
		self.party.append(self.selected_char)
		self.update_char_panels()

	def char_manage(self, character):
		print "Selected character for managing"
		self.selected_char = character
		self.update_char_panels()

	def increase_str(self, character):
		character.var_str += 1
		character.upgrade_points -= 1
		if self.char_new:
			self.update_new_character(self.manage)
		else:
			self.update_char_panels()

	def increase_dex(self, character):
		character.var_dex += 1	
		character.upgrade_points -= 1
		if self.char_new:
			self.update_new_character(self.manage)
		else:
			self.update_char_panels()

	def increase_con(self, character):
		character.var_con += 1
		character.upgrade_points -= 1
		if self.char_new:
			self.update_new_character(self.manage)
		else:
			self.update_char_panels()

	def increase_int(self, character):
		character.var_int += 1
		character.upgrade_points -= 1
		if self.char_new:
			self.update_new_character(self.manage)
		else:
			self.update_char_panels()

	def save_team1(self, team):
		if self.team1_btn.selected:
			self.team2_btn.select()
			self.team1_btn.unselect()
			self.team1 = self.team
			self.team = self.team2
			self.update_char_panels()

	def save_team2(self, team):
		if self.team2_btn.selected:
			self.team1_btn.select()
			self.team2_btn.unselect()
			self.team2 = self.team
			self.team = self.team1
			self.update_char_panels()

	def start_hotseat_game(self, none):
		log_stats('play')
		print self.players
		teams = []
		for i in range(len(self.players)):
			teams.append((self.players[i].name, self.players[i].team))
		mapsel = MapSelection(self.screen, 'map_new.txt')
		mapsel.loop()
		start_game(self.screen, mapsel.mapname, teams)

	def connect_server(self, none):
		#log_stats('join')
		#if self.player == None:
		#	print "Create player before connecting"
		#else:
		#	join_game(self.screen, self.ip_input.value, int(self.port_input.value), self.player.team)
		self.network_connected = True
		self.network_playerlist_all= NameList(self.network_con, (10, 80), (100, 200), self.networkplayers, selected = self.select_network_player)
		self.network_playerlist_selected = NameList(self.network_con, (120, 80), (100, 95), self.selected_networkplayers)
		self.network_challengelist = NameList(self.network_con, (120, 185), (100, 95), [])
		self.network_messages = TextList(self.network_con, (10, 290), (210, 70), [])
		self.network_messages.scroll.knob.rel_pos = self.network_messages.scroll.leeway
		self.sprites.add(self.network_playerlist_all)
		self.sprites.add(self.network_playerlist_selected)
		self.sprites.add(self.network_challengelist)
		self.sprites.add(self.network_messages)
		self.update_text_fields()
		self.show_network_panel()
		self.network_con.draw()
		self.lounge = LoungeConnection(self, self.ip_input.value, int(self.port_input.value))

	def disconnect_server(self, none):
		self.lounge.close()
		self.handle_disconnect()

	def handle_disconnect(self):
		self.lounge = None
		self.networkplayers[:] = []
		self.network_connected = False
		self.server = None
		self.sprites.remove(self.network_playerlist_all)
		self.sprites.remove(self.network_playerlist_selected)
		self.sprites.remove(self.network_challengelist)
		self.sprites.remove(self.network_messages)
		self.network_playerlist_all = None
		self.network_playerlist_selected = None
		self.network_challengelist = None
		self.network_messages = None
		self.update_text_fields()
		self.ip_input.value = DEFAULT_CENTRAL_HOST
		self.port_input.value = "33333"
		self.show_connect_panel()

	def send_challenge(self, none):
		try:
			c = Challenge(self.selected_networkplayers + self.player)
		except TypeError:
			print "Cannot send challenge, you must have local player selected by now"
			sys.exit(0)
		for p in self.selected_networkplayers:
			print "Sent challenge " + c + " to " + p.name
		###XXX Add challenge sending here

	def accept_challenge(self, c):
		self.selected_networkplayers = c.players
		self.show_network_panel()

	def ready_server(self, none):
		print "Player is ready"
		###XXX Add ready-sending activities here

	def host_server(self, none):
		log_stats('host')
		mapsel = MapSelection(self.screen, 'map_new.txt')
		mapsel.loop()
		host_game(self.screen, int(self.port_input.value), mapsel.mapname, self.player.team)

	def start_game(self, team):
		log_stats('play')
		teams = [(player.name, player.team) for player in self.players]
		mapsel = MapSelection(self.screen, 'map_new.txt')
		mapsel.loop()
		start_game(self.screen, mapsel.mapname, teams)

	def join_game(self, team):
		log_stats('join')
		mapsel = MapSelection(self.screen, network=True)
		mapsel.loop()
		join_game(self.screen, mapsel.ip_input.value, int(mapsel.port_input.value), team)

	def host_game(self, team):
		log_stats('host')
		mapsel = MapSelection(self.screen, 'map_new.txt', network=True, network_host=True, ip = self.ip)
		mapsel.loop()
		host_game(self.screen, int(mapsel.port_input.value), mapsel.mapname, team)

	def add_player(self, none):
		name = self.player_input.value
		if name != "":
#			print "Adding player: ", name
			self.player_input.value = ""
			player_party = []
			player_inventory = []
			for i in range(5):
				char = Character.random()
				player_party.append(char)
			for i in range(3):
				sword = random.choice(weapons.values())
				player_inventory.append(sword)
			for i in range(1):
				armor = random.choice(armors.values())
				player_inventory.append(armor)

			self.saved_players.append(Player(name, player_party, player_inventory, 1000))

	def select_network_player(self, namelist, event):
		self.network_playerlist_selected.replace([namelist.items[sel] for sel in sorted(namelist.sel)])

	def select_saved_player(self, namelist, event):
		self.local_playerlist.replace([namelist.items[sel] for sel in sorted(namelist.sel)])
		if self.player and self.player not in self.local_playerlist.items:
			self.select_player(self.local_playerlist, None)

	def select_player(self, namelist, event):
		sel = namelist.get_selected()
		if sel is not None:
			player = namelist.items[sel]
			self.manage_player(player)
		else:
			# "Unmanage" player
			self.player = None
			self.team = []
			self.party_con.clear()
			self.team_con.clear()
			self.manage.clear()
			self.inventory_con.clear()
			self.char_inventory_con.clear()

	def manage_player(self, player):
		if self.player != None:
			self.player.team = self.team

#		print "Selected player, parameters: ", parm

#		player = parm[0]
#		btn = parm[1]

#		for b in self.local_con_buttons:
#			b.unselect()
#		btn.select()

#		print "Selected another player: ", player, player.name, player.characters, player.inventory, player.money

		self.player = player
		self.team = self.player.team

		self.party = self.player.characters
		self.team = self.player.team
		self.inventory = self.player.inventory
		self.char_inventory = []

		self.selected_char = None
		self.selected_item = None
		self.update_char_panels()
		self.update_store()
		self.update_general_texts()
		self.update_inventories()

	def disconnect(self):
		self.network_connected = False
		self.update_text_fields()
		self.show_connect_panel()
		self.network_con.draw(False)

	def enable_buttons(self, i):
		for b in range(1, len(self.parent_buttons[i])):
			self.parent_buttons[i][b].toggle_visibility()

	def click(self, event):
		for b in self.manager_buttons:
			if b.contains(*event.pos):
				f = b.function[0]
				f(b.function[1])
				return True
		for b in self.new_char_buttons:
			if b.contains(*event.pos):
				f = b.function[0]
				f(b.function[1])
				return True
		for b in self.manager_char_buttons:
			if b.contains(*event.pos):
				f = b.function[0]
				f(b.function[1])
				return True
		for b in self.local_con_buttons:
			if b.contains(*event.pos):
				f = b.function[0]
				f(b.function[1])
				return True
		if self.network_connected:
			for b in self.network_buttons:
				if b.contains(*event.pos):
					f = b.function[0]
					f(b.function[1])
					return True
		else:
			for b in self.connect_buttons:
				if b.contains(*event.pos):
					f = b.function[0]
					f(b.function[1])
					return True
			"""
			for b in self.network_playerlist_buttons:
				if b.contains(*event.pos):
					f = b.function[0]
					f(b.function[1])
					return True
			for b in self.network_challengelist_buttons:
				if b.contains(*event.pos):
					f = b.function[0]
					f(b.function[1])
					return True
			"""

	def container_click(self, event, container):
		i = 0
		for b in container.children:
			for c in b.child_buttons:
				if c.visible:
					if c.contains(*event.pos):
						f = c.function[0]
						f(c.function[1])
						i = 1
						break
		if i == 0:
			for b in container.children:
				if b.parent_button.contains(*event.pos):
					if b.childs_visible:
						for tmp_b in container.children:
							tmp_b.hide_buttons()
					else:
						for tmp_b in container.children:
							tmp_b.hide_buttons()
						b.enable_buttons()
						b.parent_button.visibility = True
					print "Button function:", b.function
					if b.function != None:
						f = b.function[0]
						f(b.function[1])
					break

	def draw(self):
		self.sprites.update()
		#self.sprites.clear(self.screen, self.background)
		# Update layers
		self.sprites._spritelist.sort(key = lambda sprite: sprite._layer)
		self.sprites.draw(self.screen)
		#pygame.display.flip()

	def loop(self):
		change_sound(0, load_sound('menu-old.ogg'), BGM_FADE_MS)

		while 1:
			self.screen.fill((127, 127, 127))

			if self.network_connected: self.update_network_panel()

			self.local_con.draw()
			self.network_con.draw()
			self.text_con.draw()
			self.manage.draw()
			self.party_con.draw()
			self.inventory_con.draw()
			self.team_con.draw()
			self.char_inventory_con.draw()
			self.store_con.draw()
			self.item_con.draw()
			self.draw()
			pygame.display.flip()


			events = pygame.event.get()
			for event in events:
				for sprite in self.sprites:
					if hasattr(sprite, 'event'):
						sprite.event(event)
				if event.type == pygame.MOUSEBUTTONDOWN:
					if event.button == 1:
						self.click(event)
						self.container_click(event, self.local_con)
						self.container_click(event, self.network_con)
						self.container_click(event, self.inventory_con)
						self.container_click(event, self.party_con)
						self.container_click(event, self.manage)
						self.container_click(event, self.team_con)
						self.container_click(event, self.char_inventory_con)
						self.container_click(event, self.store_con)
						self.container_click(event, self.item_con)
						self.container_click(event, self.text_con)
				elif event.type == pygame.QUIT:
					sys.exit()

			asyncore.loop(count=1, timeout=0.0)
			time.sleep(0.05)

if __name__ == "__main__":
	screen = init_pygame()
	win = Manager(screen)
	win.loop()

