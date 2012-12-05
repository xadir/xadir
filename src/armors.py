import random

armor_data = [
	# name miss_chance% damage_reduction price
	('leather armor', 3, 2, 10),
]

class Armor:
	damage_types = ['piercing', 'slashing', 'bludgeoning', 'magic']
	def __init__(self, name, miss_chance, damage_reduction, enchanted_damage_reduction, enchanted_damage_reduction_type):
		self.name = name
		self.miss_chance = miss_chance
		self.damage_reduction = damage_reduction
		self.enchanted_damage_reduction = enchanted_damage_reduction
		self.enchanted_damage_reduction_type = enchanted_damage_reduction_type

	@classmethod
	def random(cls):
		miss_chance = random.randrange(-5, 6)
		damage_reduction = random.randrange(6)
		enchanted_damage_reduction = random.randrange(3)
		enchanted_damage_reduction_type = set([random.choice(cls.damage_types)])
		return cls(None, miss_chance, damage_reduction, enchanted_damage_reduction, enchanted_damage_reduction_type)

armors = {}
for name, miss_chance, dmg_reduct, price in armor_data:
	armors[name] = Armor(name, miss_chance, dmg_reduct, 0, set())

