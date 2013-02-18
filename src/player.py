
class Player(object):
	fields = 'name:str characters:char_list inventory:item_list money:int'
	def __init__(self, name, characters, inventory, money):
		self.name = name
		self.characters = characters
		self.inventory = inventory
		self.money = money
		self.rounds_played = 0
		self.rounds_won = 0

	@classmethod
	def random(self):
		return Player(None, [], [], 0)

