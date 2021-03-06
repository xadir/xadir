from wire import serialize, deserialize
import binascii
import asyncore
import asynchat
import socket
import debug, sys
import zlib

from game import Game, Grid, load_map, GamePlayer

VERSION = 'CENTRAL 0.3'

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

	def handle_error(self):
		debug.exchandler(*sys.exc_info())
		self.handle_close()

	def collect_incoming_data(self, data):
		self.line += data
		if len(self.line) > 1000000:
			self.die('Too much data')

	def found_terminator(self):
		line = self.line
		self.line = ''
		cmd, args = line.split(' ')
		print '<', cmd
		self.handler(cmd, zlib.decompress(binascii.unhexlify(args)))

	def push_cmd(self, cmd, args):
		data = binascii.hexlify(zlib.compress(args))
		print '>', cmd, len(args), len(data)
		self.push('%s %s\n' % (cmd, data))

	def die(self, msg):
		print 'DIE:', msg
		self.push_cmd('ERROR', serialize(msg, 'str'))
		self.handle_close()

	def handle_connect(self):
		self.push_cmd('VERSION', serialize(VERSION, 'str'))

	def handle_version(self, cmd, args):
		assert cmd == 'VERSION'
		version = deserialize(args, 'str')
		assert version == VERSION, 'local protocol version %s / remote protocol version %s' % (VERSION, version)

class XadirServerClient(CentralConnectionBase):
	def __init__(self, serv, sock):
		CentralConnectionBase.__init__(self, sock)
		self.serv = serv

		self.nicks = None
		self.client_id = self.serv.client_id
		self.serv.client_id += 1

		print 'CONNECT', self.client_id

		self.handle_connect()

	def bcast_cmd(self, cmd, args, not_to_self = True):
		for client in self.serv.clients:
			if client == self and not_to_self:
				continue
			client.push_cmd(cmd, args)

	def mcast_cmd(self, cmd, args, targets):
		for client in self.serv.clients:
			if client.client_id not in targets:
				continue
			client.push_cmd(cmd, args)

	def handle_version(self, cmd, args):
		CentralConnectionBase.handle_version(self, cmd, args)
		self.handler = self.handle_nick

	def handle_nick(self, cmd, args):
		assert cmd == 'NICK'
		self.name, self.nicks = deserialize(args, 'tuple', ['unicode', ['list', 'unicode']])
		print 'JOIN', self.client_id, self.nicks
		self.bcast_cmd('JOIN', serialize((self.client_id, self.addr[0], self.name, self.nicks), 'tuple', ['int', 'str', 'unicode', ['list', 'unicode']]))
		self.push_cmd('ID', serialize(self.client_id, 'int'))
		self.push_cmd('NICKS', serialize([(client.client_id, client.addr[0], client.name, client.nicks) for client in self.serv.clients], 'list', 'tuple', ['int', 'str', 'unicode', ['list', 'unicode']]))
		self.handler = self.handle_general

	def handle_general(self, cmd, args):
		if cmd == 'MSG':
			msg = deserialize(args, 'unicode')
			print 'MSG', self.client_id, self.nicks, repr(msg)
			self.bcast_cmd('MSG', serialize((self.client_id, msg), 'tuple', ['int', 'unicode']), not_to_self = False)
		elif cmd == 'CHALLENGE_CREATE':
			clients, map, players = deserialize(args, 'tuple', [['list', 'int'], 'str', ['list', 'Player']])
			if self.client_id in self.serv.challenges:
				self.die('Duplicate challenge')
			else:
				self.serv.challenges[self.client_id] = (map, set(clients), {self.client_id: players})
				self.mcast_cmd('CHALLENGE_CREATED', serialize((self.client_id, clients, map), 'tuple', ['int', ['list', 'int'], 'str']), self.serv.challenges[self.client_id][1])
		elif cmd == 'CHALLENGE_ACCEPT':
			client_id, players = deserialize(args, 'tuple', ['int', ['list', 'Player']])
			if self.challenge_valid(client_id):
				self.serv.challenges[client_id][2][self.client_id] = players
				self.mcast_cmd('CHALLENGE_ACCEPTED_BY', serialize((client_id, self.client_id), 'tuple', ['int', 'int']), self.serv.challenges[client_id][1])
				self.challenge_cancel_all(except_ = client_id)
				if self.serv.challenges[client_id][1] == set(self.serv.challenges[client_id][2]):
					players = [(cid, p) for cid, ps in self.serv.challenges[client_id][2].items() for p in ps]
					map, (width, height), spawns = load_map(self.serv.challenges[client_id][0])
					map = Grid(width, height, map)
					map.cell_size = (1, 1)
					map.x = map.y = 0
					game = Game(map, spawns, [])
					teams = [(p.name, None, p.team) for cid, p in players]
					spawns = game.get_spawnpoints(teams)
					class Dummy: pass
					main = Dummy()
					main.map = game.map
					main.res = None
					game.all_players = [GamePlayer(name, [(char, x, y, 0) for char, (x, y) in zip(characters, spawn)], main, None) for (name, remote, characters), spawn in zip(teams, spawns)]
					game.client_ids = self.serv.challenges[client_id][1]
					for client in self.serv.clients:
						if client.client_id not in self.serv.challenges[client_id][1]:
							continue
						client.game = game
					self.mcast_cmd('GAME_START', serialize((self.serv.challenges[client_id][0], spawns, players), 'tuple', ['str', ['list', 'list', ':coord'], ['list', 'tuple', ['int', 'Player']]]), self.serv.challenges[client_id][1])
		elif cmd == 'CHALLENGE_REJECT':
			client_id = deserialize(args, 'int')
			if self.challenge_valid(client_id):
				self.challenge_cancel(client_id, self.client_id)
		elif cmd == 'GAME_MOVE':
			p, c, t = deserialize(args, 'tuple', ['int', 'int', ':coord'])
			self.push_actions(self.game.move(self.game.all_players[p].all_characters[c], t))
		elif cmd == 'GAME_ATTACK':
			p, c, t = deserialize(args, 'tuple', ['int', 'int', ':coord'])
			self.push_actions(self.game.attack(self.game.all_players[p].all_characters[c], t))
		elif cmd == 'GAME_ENDTURN':
			self.push_actions(self.game.end_turn())
		else:
			self.die('Unknown command: ' + repr(cmd))

	def push_actions(self, actions):
		for action in actions:
			self.mcast_cmd('GAME_' + action[0] + '_RET', serialize(action[1:]), self.game.client_ids)
			assert action[0] in 'TURN MOVE ATTACK'.split()
			handler = getattr(self.game, 'handle_' + action[0].lower())
			handler(*action[1:])

	def handle_close(self):
		print 'DISCONNECT', self.client_id, self.nicks
		self.bcast_cmd('QUIT', serialize(self.client_id, 'int'))
		self.serv.clients.remove(self)
		self.challenge_cancel_all()
		self.close()

	def challenge_valid(self, client_id):
		if client_id not in self.serv.challenges:
			self.die('Unknown challenge')
			return False
		elif self.client_id not in self.serv.challenges[client_id][1]:
			self.die('Unrelated challenge')
			return False
		return True

	def challenge_cancel(self, challenger, canceler):
		self.mcast_cmd('CHALLENGE_CANCELED', serialize((challenger, canceler), 'tuple', ['int', 'int']), self.serv.challenges[challenger][1])
		del self.serv.challenges[challenger]

	def challenge_cancel_all(self, except_ = None):
		for client_id, challenge in self.serv.challenges.items():
			if client_id == except_:
				continue
			if self.client_id in challenge[1]:
				self.challenge_cancel(client_id, self.client_id)

if __name__ == '__main__':
	serv = SimpleServer(XadirServerClient)
	serv.challenges = {}
	serv.client_id = 1
	serv.set_socket(socket.socket())
	serv.set_reuse_addr()
	serv.bind(('', 33333))
	serv.listen(10)

	asyncore.loop()

