import random, os
from config import *

L = 'Light'
M = 'Medium'
H = 'Heavy'

armor_data = [
	# name type miss_chance% resilience damage_reduction price
	#T=Light/Medium/Heavy
	#                     T    M%  R   DR  P
	(u'Robe',              L,  10,  0,  0,  5),
	(u'Padded Armor',      L,   7,  1,  0,  10),
	(u'Armored Robe',      L,   5,  1,  1,  20),
	(u'Leather Armor',     M,   3,  0,  1,  20),
	(u'Studded Leather',   M,   0,  1,  2,  30),
	(u'Scale Mail',        M,  -3,  2,  2,  50),
	(u'Chainmail',         H,  -5,  1,  3,  50),
	(u'Half-Plate',        H,  -7,  2,  3,  100),
	(u'Full-Plate',        H, -10,  3,  4,  200),
]

# Graphics attributes: heading, size, style, color, type

_armor_id = 0
class Armor(object):
	damage_types = ['piercing', 'slashing', 'bludgeoning', 'magic']
	fields = 'name:unicode,NoneType miss_chance:int damage_reduction:int enchanted_damage_reduction:int enchanted_damage_reduction_type:set:str style:str price:int'
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
		name = u'armor%d' % _armor_id
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

default = Armor(u'skin', 0, 0, 0, set(), 0)

