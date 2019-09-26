import socket
from hashlib import sha1
from random import randint
from bencode import bencode, bdecode
import os, sys
import asyncio
import threading
import json

BOOTSTRAP_NODES = [
    ("router.bittorrent.com", 6881),
    ("dht.transmissionbt.com", 6881),
    ("router.utorrent.com", 6881)
] 

TID_LENGTH = 4
KRPC_TIMEOUT = 20

def entropy(bytes):
    s = ""
    for i in range(bytes):
        s += chr(randint(97, 121))
    return s
def random_id():
	hash = sha1()
	hash.update(entropy(20).encode("utf8"))
	return hash.hexdigest()

def timer(t,f):
	threading.Timer(t,f).start()

print(entropy(20))
print(random_id()[20:])

class KRPC():
	def __init__(self):
		self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		self.socket.bind(("0.0.0.0", 6881))
		print("监听")
	def send_krpc(self,msg,address):
		try:
			print(bencode(msg),address)
			self.socket.sendto(bencode(msg),address)
			pass
		except:
			pass


class Client(KRPC):
	def __init__(self):
		self.interval = 1
		self.__running = False
		KRPC.__init__(self)
	def find_node(self,address,nid=None):
		nid  = self.get_neighbor()
		tid = entropy(TID_LENGTH)
		target = random_id()[20:]
		msg={
			"t":"aa",
			"y":"q",
			"q":"find_node",
			"a":{"id":nid,"target":target}
		}
		print(msg)
		self.send_krpc(msg,address)
	def start(self):
		# self.find_node(address)
		self.joinDHT()
		while True:
			print("wait")
			try:
				(data, address) = self.socket.recvfrom(65536)
				print(type(data))
				msg = bdecode(data)
				print(type(msg))
				print(msg[b'r'][b'nodes'])
			except Exception as e:
				print(e)
				sys.exit(1)
				pass
			finally:
				self.socket.close()
				sys.exit(1)
	def get_neighbor(self):
		return random_id()[20:]
	# async def auto_find_nodes(self):
	# 	self.__running = True
	# 	while self.__running:
	# 		await asyncio.sleep(self.interval)
	# 		for nodes in BOOTSTRAP_NODES:
	# 			self.find_node(nodes)
	def joinDHT(self):
		for i in BOOTSTRAP_NODES:
			self.find_node(i)
	def timeout(self):
		self.start()
		timer(KRPC_TIMEOUT,self.timeout)


class Server(Client):
	def __init__(self):
		Client.__init__(self)
	# def ping(self,address):
	# 	nid  = self.get_neighbor()
	# 	tid = entropy(TID_LENGTH)
	# 	msg={
	# 		"t":tid,
	# 		"y":"q",
	# 		"q":"ping",
	# 		"a":{"id":nid}
	# 	}
		
	# 	self.send_krpc(msg,address)
	# 	while True:
	# 		print("wait")
	# 		try:
	# 			(data, address) = self.socket.recvfrom(65536)
	# 			msg = bdecode(data)
	# 			nodes = decode_nodes(msg["r"]["nodes"])
	# 			print(nodes)
	# 		except Exception as e:
	# 			print(e)
	# 			sys.exit(1)
	# 			pass
	# def run(self):
	# 	coroutine = self.auto_find_nodes()
	# 	loop = asyncio.get_event_loop()
	# 	task = loop.create_task(coroutine)
	# 	loop.run_until_complete(task)
D = Client()
D.timeout()
# D.timeout()
# D.ping(("router.bittorrent.com", 6881))

