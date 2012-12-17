import random
from race import races, Race
from charclass import classes, CharacterClass
from armor import armors, Armor
from weapon import weapons, Weapon

class Character(object):
	def __init__(self, name, race_name, class_name, str = 0, dex = 0, con = 0, int = 0, armor = None, weapon = None):
		self.name = name

		self.race = races[race_name]
		self.class_ = classes[class_name]

		self.var_str = str
		self.var_dex = dex
		self.var_con = con
		self.var_int = int

		self.per_wc_miss_chance = {}

		self.armor = armor
		self.weapon = weapon

	str = property(lambda self: 1 + self.race.base_str + self.var_str)
	dex = property(lambda self: 1 + self.race.base_dex + self.var_dex)
	con = property(lambda self: 1 + self.race.base_con + self.var_con)
	int = property(lambda self: 1 + self.race.base_int + self.var_int)

	max_hp = property(lambda self: self.con * 10)
	max_sp = property(lambda self: self.int)
	max_mp = property(lambda self: self.dex)

	@classmethod
	def random(cls):
		race_name = random.choice(races.keys())
		class_name = random.choice(classes.keys())
		rndstats = [random.choice(['dex', 'con', 'int', 'str']) for i in range(random.randrange(4, 6+1))]
		str = rndstats.count('str')
		dex = rndstats.count('dex')
		con = rndstats.count('con')
		int = rndstats.count('int')
		armor = Armor.random()
		weapon = random.choice(weapons.values())#Weapon.random()
		return cls(None, race_name, class_name, str, dex, con, int, armor, weapon)

