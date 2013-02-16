import random, os
from config import *

L = 'Light'
M = 'Medium'
H = 'Heavy'

armor_data = [
	# name type miss_chance% resilience damage_reduction price
	#T=Light/Medium/Heavy
	#                     T    M%  R   DR  P
	('Robe',              L,  10,  0,  0,  5),
	('Padded Armor',      L,   7,  1,  0,  10),
	('Armored Robe',      L,   5,  1,  1,  20),
	('Leather Armor',     M,   3,  0,  1,  20),
	('Studded Leather',   M,   0,  1,  2,  30),
	('Scale Mail',        M,  -3,  2,  2,  50),
	('Chainmail',         H,  -5,  1,  3,  50),
	('Half-Plate',        H,  -7,  2,  3,  100),
	('Full-Plate',        H, -10,  3,  4,  200),
]

# Graphics attributes: heading, size, style, color, type

_armor_id = 0
class Armor:
	damage_types = ['piercing', 'slashing', 'bludgeoning', 'magic']
	fields = 'name:str miss_chance:int damage_reduction:int enchanted_damage_reduction:int enchanted_damage_reduction_type:damage style:str'
	def __init__(self, name, miss_chance, damage_reduction, enchanted_damage_reduction, enchanted_damage_reduction_type, price, style = None):
		self.name = name
		self.miss_chance = miss_chance
		self.damage_reduction = damage_reduction
		self.enchanted_damage_reduction = enchanted_damage_reduction
		self.enchanted_damage_reduction_type = enchanted_damage_reduction_type
		self.price = price
		self.style = style or random.choice(file(os.path.join(GFXDIR, 'Collections/Heavy_Armor_Collection.txt')).read().replace('\n', ' ').split())

	@classmethod
	def random(cls):
		global _armor_id
		name = 'armor%d' % _armor_id
		_armor_id += 1
		miss_chance = random.randrange(-5, 6)
		damage_reduction = random.randrange(6)
		enchanted_damage_reduction = random.randrange(3)
		enchanted_damage_reduction_type = set([random.choice(cls.damage_types)])
		return cls(name, miss_chance, damage_reduction, enchanted_damage_reduction, enchanted_damage_reduction_type, 10)

	def __repr__(self):
		return 'Armor(%r, %r, %r, %r)' % (self.name, self.miss_chance, self.damage_reduction, self.enchanted_damage_reduction)

	def __str__(self):
		return '%s (miss:%d dmg:%d ench_dmg:%d%s)' % (self.name or 'Armor', self.miss_chance, self.damage_reduction, self.enchanted_damage_reduction, '/'.join(self.enchanted_damage_reduction_type))

armors = {}
for name, type, miss_chance, resilience, dmg_reduct, price in armor_data:
	armors[name] = Armor(name, miss_chance, dmg_reduct, 0, set(), price)

default = Armor('skin', 0, 0, 0, set(), 0)

