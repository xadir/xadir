import binascii
from character import Character
from weapon import Weapon
from armor import Armor
from dice import Dice

def serialize_list(items):
	result = []
	for item in items:
		type = item.__class__.__name__
		item = serialize(item)
		value = '%s:%s' % (type, binascii.hexlify(item))
		result.append(value)
	return ' '.join(result)

def deserialize_list(clss, data):
	cls_map = dict((cls.__name__, cls) for cls in clss)
	parts = data.split(' ')
	result = []

	for part in parts:
		type, name = part.split(':')
		name = binascii.unhexlify(name)
		value = deserialize(cls_map[type], name)
		result.append(value)

	return result

def serialize(self):
	result = []
	for desc in self.fields.split():
		name, type = desc.split(':')
		item = getattr(self, name)
		if item == None:
			value = '@NULL/NONE@'
		elif type in 'str int float dice':
			value = str(item)
		elif type == 'damage':
			value = '/'.join(item)
		elif type.endswith('_list'):
			value = serialize_list(item)
		else:
			value = serialize(item)
		result.append('%s=%s' % (name, binascii.hexlify(value)))
	return ' '.join(result)

def deserialize(cls, data):
	parts = data.split(' ')
	result = {}
	for part in parts:
		name, value = part.split('=')
		value = binascii.unhexlify(value)
		result[name] = value

	new = cls.random()
	for desc in cls.fields.split():
		name, type = desc.split(':')
		value = result[name]
		if value == '@NULL/NONE@':
			item = None
		elif type == 'str':
			item = str(value)
		elif type == 'int':
			item = int(value)
		elif type == 'float':
			item = float(value)
		elif type == 'dice':
			item = Dice(*map(int, value.split('d')))
		elif type == 'damage':
			item = set(value.split('/'))
		elif type == 'weapon':
			item = deserialize(Weapon, value)
		elif type == 'armor':
			item = deserialize(Armor, value)
		elif type == 'character':
			item = deserialize(Character, value)
		elif type == 'char_list':
			item = deserialize_list([Character], value)
		elif type == 'item_list':
			item = deserialize_list([Weapon, Armor], value)
		setattr(new, name, item)

	return new

