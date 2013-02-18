import random

class Dice(object):
	def __init__(self, count, sides):
		self.count = count
		self.sides = sides

	def __repr__(self):
		return '%s(%d, %d)' % (self.__class__.__name__, self.count, self.sides)

	def __str__(self):
		return '%dd%d' % (self.count, self.sides)

	def roll(self):
		result = self.count + sum(random.randrange(self.sides) for i in range(self.count))
		print self, 'rolled', result
		return result

