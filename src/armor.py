import random

armor_data = [
	# name miss_chance% damage_reduction price
	('leather armor', 3, 2, 10),
]

_armor_id = 0
class Armor:
	damage_types = ['piercing', 'slashing', 'bludgeoning', 'magic']
	fields = 'name:str miss_chance:int damage_reduction:int enchanted_damage_reduction:int enchanted_damage_reduction_type:damage'
	def __init__(self, name, miss_chance, damage_reduction, enchanted_damage_reduction, enchanted_damage_reduction_type):
		self.name = name
		self.miss_chance = miss_chance
		self.damage_reduction = damage_reduction
		self.enchanted_damage_reduction = enchanted_damage_reduction
		self.enchanted_damage_reduction_type = enchanted_damage_reduction_type

	@classmethod
	def random(cls):
		global _armor_id
		name = 'armor%d' % _armor_id
		_armor_id += 1
		miss_chance = random.randrange(-5, 6)
		damage_reduction = random.randrange(6)
		enchanted_damage_reduction = random.randrange(3)
		enchanted_damage_reduction_type = set([random.choice(cls.damage_types)])
		return cls(name, miss_chance, damage_reduction, enchanted_damage_reduction, enchanted_damage_reduction_type)

armors = {}
for name, miss_chance, dmg_reduct, price in armor_data:
	armors[name] = Armor(name, miss_chance, dmg_reduct, 0, set())

default = Armor('skin', 0, 0, 0, set())

