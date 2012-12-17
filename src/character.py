import random
from race import races, Race
from charclass import classes, CharacterClass
from armor import armors, Armor
from weapon import weapons, Weapon

class Character:
	def __init__(self, name, race_name, class_name, str = 0, dex = 0, con = 0, int = 0, armor = None, weapon = None):
		self.name = name

		self.race = races[race_name]
		self.class_ = classes[class_name]

		self.str = 1 + self.race.base_str + str
		self.dex = 1 + self.race.base_dex + dex
		self.con = 1 + self.race.base_con + con
		self.int = 1 + self.race.base_int + int

		self.per_wc_miss_chance = {}

		self.armor = armor
		self.weapon = weapon

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

