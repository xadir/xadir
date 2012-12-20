import random
from race import races, Race
from charclass import classes, CharacterClass
from armor import armors, Armor
from weapon import weapons, Weapon
import binascii

_character_id = 0
class Character(object):
	fields = 'name:str race_name:str class_name:str var_str:int var_dex:int var_con:int var_int:int armor:armor weapon:weapon'
	def __init__(self, name, race_name, class_name, str = 0, dex = 0, con = 0, int = 0, armor = None, weapon = None):
		self.name = name

		self.race_name = race_name
		self.class_name = class_name

		self.var_str = str
		self.var_dex = dex
		self.var_con = con
		self.var_int = int

		self.per_wc_miss_chance = {}

		self.armor = armor
		self.weapon = weapon

	race = property(lambda self: races[self.race_name])
	class_ = property(lambda self: classes[self.class_name])

	str = property(lambda self: 1 + self.race.base_str + self.var_str)
	dex = property(lambda self: 1 + self.race.base_dex + self.var_dex)
	con = property(lambda self: 1 + self.race.base_con + self.var_con)
	int = property(lambda self: 1 + self.race.base_int + self.var_int)

	max_hp = property(lambda self: self.con * self.class_.hp_per_con)
	max_sp = property(lambda self: self.int)
	max_mp = property(lambda self: self.dex)

	@classmethod
	def random(cls):
		global _character_id
		name = 'character%d' % _character_id
		_character_id += 1
		race_name = random.choice(races.keys())
		class_name = random.choice(classes.keys())
		rndstats = [random.choice(['dex', 'con', 'int', 'str']) for i in range(random.randrange(4, 6+1))]
		str = rndstats.count('str')
		dex = rndstats.count('dex')
		con = rndstats.count('con')
		int = rndstats.count('int')
		armor = random.choice(armors.values())#Armor.random()
		weapon = random.choice(weapons.values())#Weapon.random()
		return cls(name, race_name, class_name, str, dex, con, int, armor, weapon)

