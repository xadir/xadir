import traceback, types, sys

def saferepr(obj):
	try:
		return repr(obj)
	except:
		try:
			if isinstance(obj, (types.ClassType, types.TypeType)):
				objtype = 'class'
				info = 'class ' + obj.__module__ + '.' + obj.__name__
			elif hasattr(obj, '__class__'):
				objtype = 'instance'
				cls = obj.__class__
				info = cls.__module__ + '.' + cls.__name__ + ' instance'
			else:
				objtype = '???'
				info = object.__repr__(obj)
		except:
			objtype = '???'
			info = '???'

		return '<repr-failed-for %s at %#08x>' % (info, id(obj))

def format_exc(exctype, value, tb):
	info = ''.join(traceback.format_exception(exctype, value, tb))

	loc_info = []
	while tb:
		locs = tb.tb_frame.f_locals
		try:
			just = max(len(key) for key in locs.keys())
		except:
			just = 0
		loc_info.append('\n'.join("\t%*s: %s" % (just, key, saferepr(value)) for key, value in sorted(locs.iteritems())))

		tb = tb.tb_next

	return '\n*** Exception ***\n' + info + '\nLocals:\n' + '\nLocals:\n'.join(loc_info)

def exchandler(exctype, value, tb):
	print >>sys.stderr, format_exc(exctype, value, tb)

def backtrace():
	traceback.print_stack()

#sys.excepthook = exchandler

