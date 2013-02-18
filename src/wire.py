import binascii
from player import Player
from character import Character
from weapon import Weapon
from armor import Armor
from dice import Dice

def serialize_basic(kind, value):
	return str(value)

def deserialize_basic(kind, value):
	return allowed[kind][0](value)

def serialize_iter(kind, value, *itemkinds):
	if itemkinds and isinstance(itemkinds[0], list):
		assert len(itemkinds) == 1, 'Further specifications will be ignored'
		assert len(value) == len(itemkinds[0])
		return ' '.join(serialize_value(item, itemkind) for itemkind, item in zip(itemkinds[0], value))
	else:
		return ' '.join(serialize_value(item, *itemkinds) for item in value)

def deserialize_iter(kind, data, *itemkinds):
	if itemkinds and isinstance(itemkinds[0], list):
		assert len(itemkinds) == 1, 'Further specifications will be ignored'
		items = data.split(' ')
		assert len(items) == len(itemkinds[0])
		return allowed[kind][0](deserialize_value(item, itemkind) for itemkind, item in zip(itemkinds[0], items))
	else:
		return allowed[kind][0](deserialize_value(item, *itemkinds) for item in data.split())

def serialize_dict(kind, value, *itemkinds):
	return serialize_iter(kind, value.items(), *itemkinds)

def get_obj_spec(kind):
	spec = {}
	cls = allowed[kind][0]
	for field in cls.fields.split():
		types = field.split(':')
		name = types.pop(0)
		types = [(list if kind.startswith('#') else tuple)(kind.split(',')) for kind in types]
		spec[name] = types
	return spec

def serialize_obj(kind, value):
	spec = get_obj_spec(kind)
	return ' '.join('='.join([serialize_value(name, 'str'), serialize_value(getattr(value, name), *types)]) for name, types in spec.items())

def deserialize_obj(kind, data):
	class tmp(object): pass
	new = tmp()
	new.__class__ = allowed[kind][0]
	spec = get_obj_spec(kind)
	for item in data.split():
		name, value = item.split('=')
		name = deserialize_value(name, 'str')
		types = spec.pop(name)
		value = deserialize_value(value, *types)
		setattr(new, name, value)
	assert not spec, 'Some values missing: %r' % (spec, )
	return new

NoneType = type(None)

allowed = {
	'NoneType':  (NoneType,  lambda kind, value: '',              lambda kind, value: None),
	'bool':      (bool,      lambda kind, value: str(int(value)), lambda kind, value: bool(int(value))),
	'int':       (int,       serialize_basic,                     deserialize_basic),
	'str':       (str,       serialize_basic,                     deserialize_basic),
	'float':     (float,     serialize_basic,                     deserialize_basic),
	'tuple':     (tuple,     serialize_iter,                      deserialize_iter),
	'list':      (list,      serialize_iter,                      deserialize_iter),
	'set':       (set,       serialize_iter,                      deserialize_iter),
	'dict':      (dict,      serialize_dict,                      deserialize_iter),
	'Dice':      (Dice,      serialize_obj,                       deserialize_obj),
	'Weapon':    (Weapon,    serialize_obj,                       deserialize_obj),
	'Armor':     (Armor,     serialize_obj,                       deserialize_obj),
	'Character': (Character, serialize_obj,                       deserialize_obj),
	'Player':    (Player,    serialize_obj,                       deserialize_obj),
}

def assert_kind(kind_, kind = None, *future_kinds):
	if kind is not None:
		if isinstance(kind, tuple):
			assert kind_ in kind, '%r not in %r' % (kind_, kind)
		else:
			assert kind_ == kind, '%r != %r' % (kind_, kind)

def serialize_value(value, *types):
	kind = value.__class__.__name__
	assert_kind(kind, *types)
	data = allowed[kind][1](kind, value, *types[1:])
	return ':'.join(map(binascii.hexlify, [kind, data]))

def deserialize_value(kind_data, *types):
	kind, data = map(binascii.unhexlify, kind_data.split(':'))
	assert_kind(kind, *types)
	value = allowed[kind][2](kind, data, *types[1:])
	return value

def serialize(value):
	return serialize_value(value)

def deserialize(cls, value):
	return deserialize_value(value, cls.__name__)

