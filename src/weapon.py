import random
from dice import Dice

# Type
M = 'melee'
R = 'ranged'
Z = 'magic' # "zap"

# Size
L = 'light'
N = 'medium' # "normal"
H = 'heavy'

# Damage type
P = 'piercing'
S = 'slashing'
B = 'bludgeoning'
Z = 'magic' # "zap"

weapon_data = [
	#                                 |    damage    |    critical    |   range   |
	# name              | type | size | type | roll  |  mult | chance | min | max | price
	# before final release add reload time to crossbows
	(u'Potato', 			  R,     L,     [B],    '1d1',  2.0,    3,       1,    2,     0), 
	(u'Carrot',            M,     L,     [P],    '1d1',  2.0,    3,       0,    0,     0),
	(u'Rapier',            M,     L,     [P],    '1d6',  1.5,   10,       0,    0,    10),
	(u'Dagger',            M,     L,     [P,S],  '1d4',  1.5,   15,       0,    0,     5),
	(u'Throwing Dagger',   R,     L,     [P],    '1d4',  1.5,    2,       0,    3,    10),
	(u'Handaxe',           M,     L,     [S],    '1d6',  2.0,    2,       0,    0,    10),
	(u'Short Sword',       M,     L,     [S],    '1d6',  1.5,    8,       0,    0,    10),
	(u'Light Mace',        M,     L,     [B],    '1d6',  1.7,    5,       0,    0,    10),
	(u'Sling',             R,     L,     [B],    '1d4',  1.5,    5,       1,    5,    10),
	(u'Wand',              Z,     L,     [M],    '1d6',  1.5,    5,       0,   10,    10),
	(u'Morningstar',       M,     N,     [B,P],  '1d8',  2.0,    1,       0,    0,    10),
	(u'Battleaxe',         M,     N,     [S],    '1d8',  3.0,    1,       0,    0,    10),
	(u'Scimitar',          M,     N,     [S],    '1d6',  1.5,   10,       0,    0,    10),
	(u'Longsword',         M,     N,     [S],    '1d8',  2.0,    5,       0,    0,    10),
	(u'Warhammer',         M,     N,     [B],    '1d8',  2.5,    1,       0,    0,    10),
	(u'Flail',             M,     N,     [B],    '1d6',  2.0,    1,       0,    0,    10),
	(u'Staff',             Z,     N,     [M],    '1d8',  1.5,    5,       1,   10,    10),
	(u'Light Crossbow',    R,     N,     [P],    '1d8',  2.5,    1,       1,    8,    10),
	(u'Shortbow',          R,     N,     [P],    '1d6',  2.0,    2,       1,   10,    10),
	(u'Scythe',            M,     H,     [P,S],  '2d4',  4.0,    1,       0,    0,    10),
	(u'Spear',             M,     H,     [P],   '1d10',  2.0,    5,       0,    1,    10),
	(u'Trident',           M,     H,     [P],   '1d12',  2.5,    3,       0,    1,    10),
	(u'Halberd',           M,     H,     [P,S], '1d10',  3.0,    1,       0,    1,    10),
	(u'Greatsword',        M,     H,     [S],   '1d10',  2.5,   10,       0,    0,    10),
	(u'Greataxe',          M,     H,     [S],    '2d6',  3.0,    1,       0,    0,    10),
	(u'Heavy club',        M,     H,     [B],   '1d10',  2.5,    8,       0,    0,    10),
	(u'Heavy mace',        M,     H,     [B],   '1d12',  2.5,    5,       0,    0,    10),
	(u'Heavy Crossbow',    R,     H,     [P],   '1d10',  2.5,    1,       1,    8,    10),
	(u'Longbow',           R,     H,     [P],   '1d8',   2.0,    2,       1,   10,    10),
]

_weapon_id = 0
class Weapon(object):
	sizes = ['light', 'medium', 'heavy']
	types = ['melee', 'ranged', 'magic']
	damage_types = ['piercing', 'slashing', 'bludgeoning', 'magic']
	classes = ['sword', 'dagger', 'spear', 'axe', 'bow', 'crossbow', 'wand']
	fields = 'name:unicode,NoneType size:str type:str class_:str,NoneType damage:Dice damage_type:set:str magic_enchantment:int critical_multiplier:float critical_chance:int price:int'
	def __init__(self, name, size, type, class_, damage, damage_type, magic_enchantment, critical_multiplier = None, critical_chance = None, price = 0):
		self.name = name
		self.size = size
		self.type = type
		self.class_ = class_
		self.damage = damage
		self.damage_type = damage_type
		self.magic_enchantment = magic_enchantment
		self.critical_multiplier = critical_multiplier or {'light': 1.5, 'medium': 2.0, 'heavy': 3.0}[size]
		self.critical_chance = critical_chance or {'light': 15, 'medium': 10, 'heavy': 5}[size]
		self.price = price

	@classmethod
	def random(cls):
		global _weapon_id
		name = u'weapon%d' % _weapon_id
		_weapon_id += 1
		size = random.choice(cls.sizes)
		type = random.choice(cls.types)
		class_ = random.choice(cls.classes)
		damage = Dice(random.randrange(1, 4), random.randrange(4, 11, 2))
		damage_type = set([random.choice(cls.damage_types)])
		magic_enchantment = random.randrange(11)
		return cls(name, size, type, class_, damage, damage_type, magic_enchantment, price = 10)

	def __repr__(self):
		return 'Weapon(%r, %r, %r, %r, %r, %r, %r)' % (self.name, self.size, self.type, self.class_, self.damage, self.damage_type, self.magic_enchantment)

	def __str__(self):
		return '%s (%s %s %s %s+%d %s)' % (self.name or 'Weapon', self.size, self.type, self.class_, self.damage, self.magic_enchantment, '/'.join(self.damage_type))

weapons = {}
for name, type, size, dmg_type, dmg_roll, crit_mult, crit_chance, min_range, max_range, price in weapon_data:
	dmg_roll = Dice(*map(int, dmg_roll.split('d')))
	weapons[name] = Weapon(name, size, type, None, dmg_roll, set(dmg_type), 0, crit_mult, crit_chance, price)

default = Weapon('fist', 'light', 'melee', None, Dice(0, 0), set(['bludgeoning']), 0, 1, 0, 0)

