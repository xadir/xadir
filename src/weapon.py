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
	('rapier',            M,     L,     [P],   '1d6',   1.5,   10,      0,    0,    10),
	('dagger',            M,     L,     [P],   '1d4',   1.5,   15,      0,    0,    10),
	('throwing dagger',   R,     L,     [P],   '1d4',   1.5,   2,       0,    2,    10),
	('handaxe',           M,     L,     [S],   '1d6',   2.0,   2,       0,    0,    10),
	('short sword',       M,     L,     [S],   '1d6',   1.5,   8,       0,    0,    10),
	('light mace',        M,     L,     [B],   '1d6',   1.7,   5,       0,    0,    10),
	('sling',             R,     L,     [B],   '1d4',   1.5,   5,       1,    4,    10),
	('wand',              Z,     L,     [M],   '1d4',   1.5,   5,       0,    8,    10),
	('morningstar',       M,     N,     [B,P], '1d8',   2.0,   1,       0,    0,    10),
	('battleaxe',         M,     N,     [S],   '1d8',   3.0,   1,       0,    0,    10),
	('scimitar',          M,     N,     [S],   '1d6',   2.0,   5,       0,    0,    10),
#	('mace',              M,     N,     [B],   '?d?',   ?.?,   ?,       ?,    ?,    ?),
#	('flail',             M,     N,     [B],   '?d?',   ?.?,   ?,       ?,    ?,    ?),
#	('staff',             ?,     ?,     [?],   '?d?',   ?.?,   ?,       ?,    ?,    ?),
	('scythe',            M,     H,     [P,S], '2d4',   4.0,   1,       0,    0,    10),
#	('spear',             ?,     ?,     [?],   '?d?',   ?.?,   ?,       ?,    ?,    ?),
#	('trident',           ?,     ?,     [?],   '?d?',   ?.?,   ?,       ?,    ?,    ?),
	('halberd',           M,     H,     [P,S], '1d10',  3.0,   1,       0,    1,    10),
	('greatsword',        M,     H,     [S],   '1d10',  2.5,   10,      0,    0,    10),
	('greataxe',          M,     H,     [S],   '2d6',   3.0,   1,       0,    0,    10),
	('heavy club',        M,     H,     [B],   '1d10',  2.5,   8,       0,    0,    10),
	('heavy mace',        M,     H,     [B],   '1d12',  2.5,   5,       0,    0,    10),
]

class Weapon:
	sizes = ['light', 'medium', 'heavy']
	types = ['melee', 'ranged', 'magic']
	damage_types = ['piercing', 'slashing', 'bludgeoning', 'magic']
	classes = ['sword', 'dagger', 'spear', 'axe', 'bow', 'crossbow', 'wand']
	def __init__(self, name, size, type, class_, damage, damage_type, magic_enchantment, critical_multiplier = None, critical_chance = None):
		self.name = name
		self.size = size
		self.type = type
		self.class_ = class_
		self.damage = damage
		self.damage_type = damage_type
		self.magic_enchantment = magic_enchantment
		self.critical_multiplier = critical_multiplier or {'light': 1.5, 'medium': 2.0, 'heavy': 3.0}[size]
		self.critical_chance = critical_chance or {'light': 15, 'medium': 10, 'heavy': 5}[size]

	@classmethod
	def random(cls):
		size = random.choice(cls.sizes)
		type = random.choice(cls.types)
		class_ = random.choice(cls.classes)
		damage = Dice(random.randrange(1, 4), random.randrange(4, 11, 2))
		damage_type = set([random.choice(cls.damage_types)])
		magic_enchantment = random.randrange(11)
		return cls(None, size, type, class_, damage, damage_type, magic_enchantment)

	def __repr__(self):
		return 'Weapon(%r, %r, %r, %r, %r, %r, %r)' % (self.name, self.size, self.type, self.class_, self.damage, self.damage_type, self.magic_enchantment)

	def __str__(self):
		return '%s (%s %s %s %s+%d %s)' % (self.name or 'Weapon', self.size, self.type, self.class_, self.damage, self.magic_enchantment, '/'.join(self.damage_type))

weapons = {}
for name, type, size, dmg_type, dmg_roll, crit_mult, crit_chance, min_range, max_range, price in weapon_data:
	dmg_roll = Dice(*map(int, dmg_roll.split('d')))
	weapons[name] = Weapon(name, size, type, None, dmg_roll, set(dmg_type), 0, crit_mult, crit_chance)

default = Weapon('fist', 'light', 'melee', None, Dice(0, 0), set(['bludgeoning']), 0, 1, 0)

