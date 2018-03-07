#!/usr/bin/python3


import random

verbose=False

class Host:
	def __init__(self):
		self.ping=True

	def disconnect(self):
		self.ping=False

	def connect(self):
		self.ping=True

class Peer:
	
	def __get_ip(self):
		#global cpt
		return '%s:%s:%s:%s' % tuple([str(hex(random.randrange(0,65535)))[2:] for i in range(0,4)])
	
	def __init__(self, id_):
		self.connected=[] # list of other peers, which will be ID for now
		self.max_=10 
		self.id_=id_
		self.host=Host()
		self.host.ip=self.__get_ip()

	def add_peer(self, id_):
		if (len(self.connected) < self.max_):
			if not(id_ in self.connected):
				if id_ != self.id_:
					self.connected.append(id_)
	
	def check_peer(self): # remove unresponsive peers
		self.list_ = [i for i in self.list_ if ping(i)]

	def add_peers(self, peers): # for each peer update its own list
		for i in peers:
			self.add_peer(i)

	
				

class Peers():

		
	def connect(self, idxA, idxB, update_list): #update_list = True means we also add to each peer the one to which the other one is connected
#TODO should be an event on 'onconnect', no idea how to do that
		self.peers[idxA].add_peer(idxB)
		self.peers[idxB].add_peer(idxA)

		self.peers[idxA].add_peers(self.peers[idxB].connected)
		self.peers[idxB].add_peers(self.peers[idxA].connected)

	def __init__(self): 
		self.peers = {}
		self.add_three()
		self.add_randoms(100)
		self.disconnect_randoms(30)
		self.check_hosts()

	def add_three(self):
		for i in range(0,3): 
			p=Peer(i)
			self.peers[i]=p
			for j in range(0,i):
				self.connect(i, j, False) 

	def add_random(self): # add a host and connect to a random one
		idx=len(self.peers)
		p=Peer(idx)	
		self.peers[idx]=p
		self.connect(idx, random.randrange(idx - 1), True)
		return p

	def add_randoms(self, count):
		for i in range(0, count):
			self.add_random()

	def disconnect_random(self):
		idx=random.randrange(len(self.peers))
		self.peers[idx].host.ping=False
		return idx

	def disconnect_randoms(self, count):
		for i in range(0, count):
			self.disconnect_random()
		
	def check_hosts(self):
		for i in range(0, len(self.peers)):
			p=self.peers[i]
			if p.host.ping:
				#print("updating %d:[%s]" % (i, p.host.ip))
				self.check(i)

	def check(self, idx):
		p=self.peers[idx]
		a=p.connected
		p.connected=[i for i in p.connected if self.peers[i].host.ping]
		if verbose:
			if len(a) != len(p.connected):
				print("updated list :")
				print(a)
				print(p.connected)
		
