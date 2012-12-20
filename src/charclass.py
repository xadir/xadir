
class_data = [
	# XXX: <Insert real class data here>
	# weapon dmg, DR, RES, hit, MP, miss, crit
	#           hit miss crit RES DR MP weapon_dmg hp_per_con
	('warrior', 1,  0,   1,       1,    2,         4+8),
	('wizard',  3,  1,   0,       0,    1,         4+4),
	('rogue',   1,  3,   0,       0,    1,         4+6),
]

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

