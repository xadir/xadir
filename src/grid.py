
class Grid:
	def __init__(self, width, height, data = None, default = None):
		self.width = width
		self.height = height
		if data is None:
			data = [[default for x in range(width)] for y in range(height)]
		self.data = data

	def __getitem__(self, (x, y)):
		return self.data[y][x]

	def __setitem__(self, (x, y), value):
		self.data[y][x] = value

	def __contains__(self, (x, y)):
		return x >= 0 and y >= 0 and x < self.width and y < self.height

	def keys(self):
		for y in range(self.height):
			for x in range(self.width):
				yield (x, y)

	def values(self):
		for y in range(self.height):
			for x in range(self.width):
				yield self[x, y]

	def items(self):
		for y in range(self.height):
			for x in range(self.width):
				yield (x, y), self[x, y]

	def env_minmax(self, (x, y), size = 1):
		x_min = max(x - size, 0)
		y_min = max(y - size, 0)
		x_max = min(x + size, self.width - 1)
		y_max = min(y + size, self.height - 1)
		return x_min, x_max, y_min, y_max

	def env_keys(self, pos, size = 1):
		x_min, x_max, y_min, y_max = self.env_minmax(pos, size)
		for y in range(y_min, y_max + 1):
			for x in range(x_min, x_max + 1):
				yield (x, y)

	def env_values(self, pos, size = 1):
		x_min, x_max, y_min, y_max = self.env_minmax(pos, size)
		for y in range(y_min, y_max + 1):
			for x in range(x_min, x_max + 1):
				yield self[x, y]

	def env_items(self, pos, size = 1):
		x_min, x_max, y_min, y_max = self.env_minmax(pos, size)
		for y in range(y_min, y_max + 1):
			for x in range(x_min, x_max + 1):
				yield (x, y), self[x, y]

