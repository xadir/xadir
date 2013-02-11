
race_data = [
	# name         str dex con int hairline shoulderline size
	('human',      1,  1,  1,  1,  -2,      0,           'human'),
	('minotaur',   3,  0,  0,  0,  -6,      0,           None),
	('imp',        0,  3,  0,  0,  1,       0,           None),
	#('treant',     0,  0,  3,  0,  0,       0),
	('mindflayer', 0,  0,  0,  3,  -4,      0,           'human'),
	('orc',        2,  1,  0,  0,  0,       0,           'dwarf'),
	('ogre',       2,  0,  1,  0,  -6,      0,           None),
	('djinn',      2,  0,  0,  1,  -3,      0,           'human'),
	('thiefling',  0,  2,  1,  0,  -2,      0,           'human'),
	('elf',        0,  2,  0,  1,  -4,      0,           'elf'),
	('goblin',     1,  2,  0,  0,  1,       0,           'gnome'),
	('mummy',      0,  0,  2,  1,  -4,      0,           'human'),
	('dwarf',      1,  0,  2,  0,  1,       0,           'dwarf'),
	('werewolf',   0,  1,  2,  0,  -2,      0,           None),
	#('myconid',    1,  0,  0,  2,  0,       0),
	('gnome',      0,  1,  0,  2,  0,       0,           'gnome'),
	('vampire',    0,  0,  1,  2,  -2,      0,           'human'),
]

class Race:
	def __init__(self, name, str, dex, con, int, hairline, shoulderline, armorsize):
		self.name = name
		self.base_str = str
		self.base_dex = dex
		self.base_con = con
		self.base_int = int
		self.hairline = hairline
		self.shoulderline = shoulderline
		self.armorsize = armorsize

races = {}
for name, str, dex, con, int, hairline, shoulderline, armorsize in race_data:
	races[name] = Race(name, str, dex, con, int, hairline, shoulderline, armorsize)

