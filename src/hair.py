
class Hair:
	def __init__(self, name):
		self.name = name
		self.xoffset = self.yoffset = 0

hairs = {}

for name in 'abcdefghij':
	hairs[name] = Hair(name)

