import traceback, types, sys
import linecache, dis

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

def get_names_at(co, lasti):
	"""Get the names that are referenced in the active part of code"""
	code = co.co_code
	labels = dis.findlabels(code)
	linestarts = dict(dis.findlinestarts(co))
	n = len(code)
	i = 0
	extended_arg = 0
	free = None
	linenames = []
	found = False
	while i < n:
		c = code[i]
		op = ord(c)
		if i in linestarts:
			if found:
				return linenames
			linenames = []
		if i == lasti:
			found = True
		i = i+1
		if op >= dis.HAVE_ARGUMENT:
			oparg = ord(code[i]) + ord(code[i+1])*256 + extended_arg
			extended_arg = 0
			i = i+2
			if op == dis.EXTENDED_ARG:
				extended_arg = oparg*65536L
			if op in dis.hasname:
				linenames.append(co.co_names[oparg])
			elif op in dis.haslocal:
				linenames.append(co.co_varnames[oparg])
			elif op in dis.hasfree:
				if free is None:
					free = co.co_cellvars + co.co_freevars
				linenames.append(free[oparg])
	if found:
		return linenames

def format_exc(exctype, value, tb):
	info = ''.join(traceback.format_exception(exctype, value, tb))

	loc_info = []
	while tb:
		f = tb.tb_frame
		co = f.f_code
		active = get_names_at(co, f.f_lasti)
		linecache.checkcache(co.co_filename)
		line = linecache.getline(co.co_filename, tb.tb_lineno, f.f_globals)
		item = '  \x1b[1;32mFile "%s", line %d, in %s\x1b[m\n' % (co.co_filename, tb.tb_lineno, co.co_name)
		if line:
			item = item + '    %s\n' % line.strip()

		locs = tb.tb_frame.f_locals
		if locs == tb.tb_frame.f_globals:
			locs = dict((key, locs[key]) for key in active)

		try:
			just = max(len(key) for key in locs.keys())
		except:
			just = 0

		loc_info.append(item + '  \x1b[1;34mLocals:\x1b[m\n' + '\n'.join("    %s%-*s%s: %s" % (('\x1b[1;31m' if key in active else ''), just, key, '\x1b[m', saferepr(value)[:512]) for key, value in sorted(locs.iteritems(), key = lambda (k, v): (k not in active, k))))

		tb = tb.tb_next

	return '\n*** Exception ***\n' + info + '\n' + '\n'.join(loc_info)

def exchandler(exctype, value, tb):
	print >>sys.stderr, format_exc(exctype, value, tb)

def backtrace():
	traceback.print_stack()

#sys.excepthook = exchandler

