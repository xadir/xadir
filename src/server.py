from wire import serialize, deserialize
import binascii
import asyncore
import asynchat
import socket

VERSION = 'CENTRAL 0.1'

class SimpleServer(asyncore.dispatcher):
	def __init__(self, clientclass):
		asyncore.dispatcher.__init__(self)

		self.clientclass = clientclass
		self.clients = []

	def handle_accept(self):
		sock, addr = self.accept()
		client = self.clientclass(self, sock)
		self.clients.append(client)

class CentralConnectionBase(asynchat.async_chat):
	def __init__(self, sock):
		asynchat.async_chat.__init__(self, sock)

		self.line = ''
		self.set_terminator('\n')

		self.handler = self.handle_version

	def collect_incoming_data(self, data):
		self.line += data
		if len(self.line) > 100000:
			self.die('Too much data')

	def found_terminator(self):
		line = self.line
		self.line = ''
		cmd, args = line.split(' ')
		self.handler(cmd, binascii.unhexlify(args))

	def push_cmd(self, cmd, args):
		self.push('%s %s\n' % (cmd, binascii.hexlify(args)))

	def die(self, msg):
		self.push_cmd('ERROR', serialize(msg, 'str'))
		self.handle_close()

	def handle_connect(self):
		self.push_cmd('VERSION', serialize(VERSION, 'str'))

	def handle_version(self, cmd, args):
		assert cmd == 'VERSION'
		version = deserialize(args, 'str')
		assert version == VERSION

class XadirServerClient(CentralConnectionBase):
	def __init__(self, serv, sock):
		CentralConnectionBase.__init__(self, sock)
		self.serv = serv

		self.client_id = self.serv.client_id
		self.serv.client_id += 1

		self.handle_connect()

	def bcast_cmd(self, cmd, args, not_to_self = True):
		for client in self.serv.clients:
			if client == self and not_to_self:
				continue
			client.push_cmd(cmd, args)

	def handle_version(self, cmd, args):
		CentralConnectionBase.handle_version(self, cmd, args)
		self.handler = self.handle_nick

	def handle_nick(self, cmd, args):
		assert cmd == 'NICK'
		self.nicks = deserialize(args, 'list', 'str')
		self.bcast_cmd('JOIN', serialize((self.client_id, self.addr[0], self.nicks), 'tuple', ['int', 'str', ['list', 'str']]))
		self.push_cmd('ID', serialize(self.client_id, 'int'))
		self.push_cmd('NICKS', serialize([(client.client_id, client.addr[0], client.nicks) for client in self.serv.clients], 'list', 'tuple', ['int', 'str', ['list', 'str']]))
		self.handler = self.handle_general

	def handle_general(self, cmd, args):
		if cmd == 'MSG':
			msg = deserialize(args, 'str')
			print self.client_id, self.nicks, repr(msg)
			self.bcast_cmd('MSG', serialize((self.client_id, msg), 'tuple', ['int', 'str']), not_to_self = False)
		else:
			self.die('Unknown command: ' + repr(cmd))

	def handle_close(self):
		self.bcast_cmd('QUIT', serialize(self.client_id, 'int'))
		self.serv.clients.remove(self)
		self.close()

if __name__ == '__main__':
	serv = SimpleServer(XadirServerClient)
	serv.client_id = 1
	serv.set_socket(socket.socket())
	serv.set_reuse_addr()
	serv.bind(('', 33333))
	serv.listen(10)

	asyncore.loop()

