import socket
from hashlib import sha1
from random import randint
from bencode import bencode, bdecode
import os, sys
import asyncio

BOOTSTRAP_NODES = [
    ("router.bittorrent.com", 6881),
    ("dht.transmissionbt.com", 6881),
    ("router.utorrent.com", 6881)
] 

TID_LENGTH = 4

def entropy(bytes):
    s = ""
    for i in range(bytes):
        s += chr(randint(97, 121))
    return s
def random_id():
	hash = sha1()
	hash.update(entropy(20).encode("utf8"))
	return hash.hexdigest()

class KRPC():
	def __init__(self):
		self.socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		self.socket.bind(("0.0.0.0", 8888))
		print("监听")
	def send_krpc(self,msg,address):
		try:
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
		target = self.get_neighbor()
		msg={
			"t":tid,
			"y":"q",
			"q":"find_node",
			"a":{"id":nid,"target":target}
		}
		print(msg)
		self.send_krpc(msg,address)
	def start(self,address):
		self.find_node(address)
		while True:
			print("wait")
			try:
				(data, address) = self.socket.recvfrom(65536)
				print(data)
			except:
				print("except")
				sys.exit(1)
				pass
	def get_neighbor(self):
		return random_id()[20:]
	async def auto_find_nodes(self):
		self.__running = True
		while self.__running:
			await asyncio.sleep(self.interval)
			for nodes in BOOTSTRAP_NODES:
				self.find_node(nodes)

class DHTServer(Client):
	def __init__(self):
		Client.__init__(self)
	def ping(self,address):
		nid  = self.get_neighbor()
		tid = entropy(TID_LENGTH)
		msg={
			"t":tid,
			"y":"q",
			"q":"ping",
			"a":{"id":nid}
		}
		print(msg)
		self.send_krpc(msg,address)
		while True:
			print("wait")
			try:
				(data, address) = self.socket.recvfrom(65536)
				print(data,address)
			except Exception as e:
				print(e)
				sys.exit(1)
				pass
	def run(self):
		coroutine = self.auto_find_nodes()
		loop = asyncio.get_event_loop()
		task = loop.create_task(coroutine)
		loop.run_until_complete(task)
D = DHTServer()
D.run()

