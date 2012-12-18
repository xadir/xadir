
terrain_data = [
	# name     short miss_chance
	('ground', 'G',  0),
	('dirt',   'D',  0),
	('forest', 'F',  10),
	('water',  'W',  0),
]

class Terrain:
	def __init__(self, name, short, miss_chance):
		self.name = name
		self.short = short
		self.miss_chance = miss_chance

terrains = {}
for name, short, miss_chance in terrain_data:
	terrains[short] = Terrain(name, short, miss_chance)

