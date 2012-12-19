
class_data = [
	# XXX: <Insert real class data here>
	# weapon dmg, DR, RES, hit, MP, miss, crit
	# hit, miss, crit, RES, DR, MP, weapon dmg
	('warrior', 0),
	('mage',    0),
	('healer',  0),
]

class CharacterClass:
	def __init__(self, name, damage_reduction):
		self.name = name
		self.damage_reduction = damage_reduction

classes = {}
for name, damage_reduction in class_data:
	classes[name] = CharacterClass(name, damage_reduction)

