
race_data = [
	# name         str dex con int
	('human',      1,  1,  1,  1),
	('minotaur',   3,  0,  0,  0),
	('imp',        0,  3,  0,  0),
	#('treant',     0,  0,  3,  0),
	('mindflayer', 0,  0,  0,  3),
	#('orc',        2,  1,  0,  0),
	('ogre',       2,  0,  1,  0),
	('djinn',      2,  0,  0,  1),
	('thiefling',  0,  2,  1,  0),
	('elf',        0,  2,  0,  1),
	('goblin',     1,  2,  0,  0),
	('mummy',      0,  0,  2,  1),
	('dwarf',      1,  0,  2,  0),
	('werewolf',   0,  1,  2,  0),
	#('myconid',    1,  0,  0,  2),
	('gnome',      0,  1,  0,  2),
	('vampire',    0,  0,  1,  2),
]

class Race:
	def __init__(self, name, str, dex, con, int):
		self.name = name
		self.base_str = str
		self.base_dex = dex
		self.base_con = con
		self.base_int = int

races = {}
for name, str, dex, con, int in race_data:
	races[name] = Race(name, str, dex, con, int)

