#!/usr/bin/python3


import random

verbose=False
min_hosts=10
max_hosts=20

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
	
	def __init__(self, idx, peers):
		self.connected=[] # list of other peers, which will be ID for now
		self.idx=idx
		self.host=Host()
		self.host.ip=self.__get_ip()
		self.info=None
		self.peers=peers # pointer to the list of other peers

	def add_peer(self, idx):
		if self.idx!=idx and not(idx in self.connected):
			if len(self.connected) < max_hosts:
				self.connected.append(idx)
				self.peers[idx].connected.append(self.idx)
				return True
			else:
				return False 
		else:
			return False

	def connect_to_other_s_peers(self):
		if len(self.connected) < min_hosts:
			l=[]
			for i in self.connected:
				o=self.peers[i]
				if o.host.ping:
					for j in o.connected:
						l.append(j)
			while len(l)>0 and len(self.connected) < min_hosts: 
				self.add_peer(l.pop(0))

	def disconnect_from_offline(self): # remove unresponsive peers
		l = [] # new list 	
		for i in self.connected:
			if self.peers[i].host.ping:
				l.append(i)
		self.connected = l

	def check_connections(self, peers):
		self.disconnect_from_offline()
		self.connect_to_other_s_peers()

	def init_calculation(self, value): 
		self.tick=random.randrange(10,30)

	def check_calculation(self, value):
		pass

	def init_info(self, info):
		self.info=info

	def pass_info(self, peers):
		# that host will ask all the other the value
		if self.info != None:
			for i in self.connected:
				if peers[i].info != self.info:
					peers[i].info = self.info	

class Peers(): 
	def __init__(self): 
		self.peers = []
		self.add_randoms(10000)
		self.check_till_stable()
		#self.disconnect_randoms(30)
		#self.check_till_stable()

	def add_three(self):
		for i in range(0,3): 
			p=Peer(i, self.peers)
			self.peers.append(p)
			for j in range(0,i):
				self.connect(i, j) 

	def add_random(self): # add a host and connect to a random one
		idx=len(self.peers)
		p=Peer(idx, self.peers)	
		self.peers.append(p)
		if len(self.peers)>1:
			while True:
				if p.add_peer(random.choice(self.peers).idx):
					break

		return p

	def add_randoms(self, count):
		for i in range(0, count):
			self.add_random()

	def disconnect_random(self):
		random.choice(self.peers).host.ping=False

	def disconnect_randoms(self, count):
		for i in range(0, count):
			self.disconnect_random()
		
	def check_connections(self):
		for p in self.peers:
			if p.host.ping:
				p.check_connections(self.peers)	
	
	def avg_connected_size(self):
		b=[len(p.connected) for p in self.peers]
		return (sum(b))/float(len(b))

	def check_till_stable(self):
		a=0
		while a!=self.avg_connected_size():
			a=self.avg_connected_size()
			print("avg size = %d" % a)
			self.check_connections()

	def calcuation(self):
		pass

	def check_info(self, info):
		# display the percentage of peers having a given info
		online=[a for a in self.peers if a.host.ping]
		a=len([a for a in online if (a.info==info)])
		b=len(online)
		return float(a)/float(b)

	def pass_info(self, info):
		random.choice(self.peers).init_info(info)
		self.check_info(info)
		p=0 # percentage of computers having the info
		oldp=0
		c=0 # max ticks before we call it a failure
		while (p<1) and (c<200) and ((p!=oldp) or c==0): # we check also percentage to get higher
			oldp=p
			c=c+1 # to limit the number of loops
			for i in self.peers:
				i.pass_info(self.peers)
			p=self.check_info(info)
			print("percentage is %0.2f" % (p*100))

def try_():
	a=Peers()
	a.pass_info(5)
	return a
