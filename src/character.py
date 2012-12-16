import random
from race import races, Race
from charclass import classes, CharacterClass
from armor import armors, Armor
from weapon import weapons, Weapon

class Character:
	def __init__(self, name, race_name, class_name, str, dex, con, int, armor, weapon):
		self.name = name

		self.race = races[race_name]
		self.class_ = classes[class_name]

		self.str = 1 + self.race.base_str + str
		self.dex = 1 + self.race.base_dex + dex
		self.con = 1 + self.race.base_con + con
		self.int = 1 + self.race.base_int + int

		self.max_hp = self.con * 10
		self.max_sp = self.int
		self.max_mp = self.dex

		self.per_wc_miss_chance = {}

		self.armor = armor
		self.weapon = weapon

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

