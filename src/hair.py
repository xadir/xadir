
hair_data = [
	('a', 0, 0),
	('b', 0, 0),
	('c', 0, -2),
	('d', 0, -1),
	('e', 0, 0),
	('f', 0, 0),
	('g', 0, -1),
	('h', 1, 0),
	('i', 0, -3),
	('j', 1, -2),
]

class Hair:
	def __init__(self, name, xoffset = 0, yoffset = 0):
		self.name = name
		self.xoffset = xoffset
		self.yoffset = yoffset

hairs = {}

for name, xoff, yoff in hair_data:
	hairs[name] = Hair(name, xoff, yoff)

