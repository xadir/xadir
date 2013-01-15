import threading
import urllib
import re
import binascii
from config import *

class IpResolver(threading.Thread):
	def __init__(self, name, win = None):
		threading.Thread.__init__(self)
		self.win = win
		self.name = name

	def run(self):
		query = ''
		if TRACK_USAGE:
			query = '?' + str(int(binascii.hexlify(self.name), 16))

		data = urllib.urlopen('http://whatismyip.xadir.net/plain' + query).read()
		data = data.strip()
		if self.win and re.match('^\\d+[.]\\d+[.]\\d+[.]\\d+$', data):
			self.win.ip = data

def log_stats(name):
	if TRACK_USAGE:
		IpResolver(name).start()

