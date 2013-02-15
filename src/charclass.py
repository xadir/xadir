
class_data = [
	# XXX: <Insert real class data here>
	# weapon dmg, DR, RES, hit, MP, miss, crit
	#           hit miss crit RES DR MP weapon_dmg hp_per_con
	('warrior', 1,  0,   1,       1,    2,         4+8),
	('wizard',  3,  1,   0,       0,    1,         4+4),
	('rogue',   1,  3,   0,       0,    1,         4+6),
]

level_up = [
	# defines what character gets with level up
	# class     level  xp     hit miss crit RES DR MP weapon_dmg hp_per_con
	('warrior', 1,     100,  0,  0,   0,   0,  0, 0, 1,         0),
	('warrior', 2,     2000,  0,  0,   0,   0,  1, 0, 1,         0),
	('warrior', 3,     3000,  0,  0,   0,   1,  1, 0, 1,         0),
	('warrior', 4,     4000,  0,  0,   0,   1,  1, 0, 2,         0),
	('warrior', 5,     5000,  0,  0,   0,   1,  2, 0, 2,         0),
	('warrior', 6,     6000,  0,  0,   0,   2,  2, 0, 2,         0),
	('warrior', 7,     7000,  0,  0,   0,   2,  2, 0, 3,         0),
	('warrior', 8,     8000,  0,  0,   0,   2,  3, 0, 3,         0),
	('warrior', 9,     9000,  0,  0,   0,   3,  3, 0, 3,         0),
	('warrior', 10,    10000, 0,  0,   0,   3,  3, 0, 4,         0),
	('wizard',  1,     100,  1,  0,   0,   0,  0, 0, 0,         0),
	('wizard',  2,     2000,  1,  0,   0,   0,  1, 0, 0,         0),
	('wizard',  3,     3000,  2,  0,   0,   0,  1, 0, 1,         0),
	('wizard',  4,     4000,  2,  0,   0,   0,  1, 0, 1,         0),
	('wizard',  5,     5000,  3,  0,   0,   0,  1, 0, 1,         0),
	('wizard',  6,     6000,  3,  0,   0,   0,  1, 0, 1,         0),
	('wizard',  7,     7000,  4,  0,   0,   0,  2, 0, 2,         0),
	('wizard',  8,     8000,  4,  0,   0,   0,  2, 0, 2,         0),
	('wizard',  9,     9000,  5,  0,   0,   0,  2, 0, 2,         0),
	('wizard',  10,    10000, 5,  0,   0,   0,  2, 0, 2,         0),
	('rogue',   1,     100,  0,  0,   0,   0,  0, 1, 0,         0),
	('rogue',   2,     2000,  0,  1,   0,   0,  0, 1, 0,         0),
	('rogue',   3,     3000,  0,  1,   1,   0,  0, 1, 0,         0),
	('rogue',   4,     4000,  0,  2,   1,   0,  0, 2, 0,         0),
	('rogue',   5,     5000,  0,  2,   2,   0,  0, 2, 0,         0),
	('rogue',   6,     6000,  0,  3,   2,   0,  0, 2, 0,         0),
	('rogue',   7,     7000,  0,  3,   3,   0,  0, 3, 0,         0),
	('rogue',   8,     8000,  0,  4,   3,   0,  0, 3, 0,         0),
	('rogue',   9,     9000,  0,  4,   4,   0,  0, 3, 0,         0),
	('rogue',   10,    10000, 0,  5,   4,   0,  0, 3, 0,         0)
]

win_xp = 150
defeat_xp = 75

class CharacterClass:
	def __init__(self, name, hit, miss, crit, damage_reduction, weapon_damage, hp_per_con):
		self.name = name
		self.hit_chance = hit
		self.miss_chance = miss
		self.crit_chance = crit
		self.damage_reduction = damage_reduction
		self.weapon_damage = weapon_damage
		self.hp_per_con = hp_per_con

classes = {}
for name, hit, miss, crit, damage_reduction, weapon_damage, hp_per_con in class_data:
	classes[name] = CharacterClass(name, hit, miss, crit, damage_reduction, weapon_damage, hp_per_con)

