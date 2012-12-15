from races import races, Race

class Character:
	def __init__(self, name, race_name, class_name, str, dex, con, int):
		self.name = name
		self.race = races[race_name]
		self.class_ = None
		self.str = 1 + self.race.base_str + str
		self.dex = 1 + self.race.base_dex + dex
		self.con = 1 + self.race.base_con + con
		self.int = 1 + self.race.base_int + int

		self.max_hp = self.con * 10
		self.max_sp = self.int
		self.max_mp = self.dex

	@classmethod
	def random(cls):
		rndstats = [random.choice(['dex', 'con', 'int', 'str']) for i in range(random.randrange(4, 6+1))]
		str = rndstats.count('str')
		dex = rndstats.count('dex')
		con = rndstats.count('con')
		int = rndstats.count('int')
		return cls(None, random.choice(races.keys()), None, str, dex, con, int)

