import random
from armor import armors, Armor
from weapon import weapons, Weapon

class Store:
	def __init__(self, init_item_count = 20, money = 2000):
		self.init_item_count = init_item_count
		self.money = money
		self.items = []

		for i in range(self.init_item_count):
			self.items.append(random.choice(armors.values()+weapons.values()))

	def sell_item_to_store(self, item):
		self.items.append(item)
		self.money -= item.price

	def buy_item_from_store(self, item):
		self.items.remove(item)
		self.money += item.price
