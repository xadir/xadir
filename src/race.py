
race_data = [
	# name         str dex con int hairline shoulderline
	('human',      1,  1,  1,  1,  1,       5),
	('minotaur',   3,  0,  0,  0,  1,       5),
	('imp',        0,  3,  0,  0,  1,       5),
	#('treant',     0,  0,  3,  0,  None,    None),
	('mindflayer', 0,  0,  0,  3,  None,    None),
	('orc',        2,  1,  0,  0,  None,    None),
	('ogre',       2,  0,  1,  0,  None,    None),
	('djinn',      2,  0,  0,  1,  None,    None),
	('thiefling',  0,  2,  1,  0,  None,    None),
	('elf',        0,  2,  0,  1,  None,    None),
	('goblin',     1,  2,  0,  0,  None,    None),
	('mummy',      0,  0,  2,  1,  None,    None),
	('dwarf',      1,  0,  2,  0,  None,    None),
	('werewolf',   0,  1,  2,  0,  None,    None),
	#('myconid',    1,  0,  0,  2,  None,    None),
	('gnome',      0,  1,  0,  2,  None,    None),
	('vampire',    0,  0,  1,  2,  None,    None),
]

class Race:
	def __init__(self, name, str, dex, con, int, hairline, shoulderline):
		self.name = name
		self.base_str = str
		self.base_dex = dex
		self.base_con = con
		self.base_int = int
		self.hairline = hairline
		self.shoulderline = shoulderline

races = {}
for name, str, dex, con, int, hairline, shoulderline in race_data:
	races[name] = Race(name, str, dex, con, int, hairline, shoulderline)

