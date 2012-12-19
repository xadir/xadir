import asyncore
import asynchat
import binascii

class Messager(asynchat.async_chat):
	def __init__(self, handle_message, sock=None):
		asynchat.async_chat.__init__(self, sock=sock)
		self.handle_message = handle_message
		self.line = ''
		self.set_terminator('\n')

	def collect_incoming_data(self, data):
		print 'INCOMING:', repr(data)
		self.line += data

	def found_terminator(self):
		print 'TERMINATOR'
		line = self.line
		self.line = ''
		self.handle_line(line)

	def handle_line(self, line):
		msg_type, msg_data = line.split()
		msg_data = binascii.unhexlify(msg_data)
		self.handle_message(msg_type, msg_data)

	def push_message(self, msg_type, msg_data):
		self.push('%s %s\n' % (msg_type, binascii.hexlify(msg_data)))

	def handle_connect(self):
		self.handle_message('CONNECTED', '')

	def handle_close(self):
		self.close()

