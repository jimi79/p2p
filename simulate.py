#!/usr/bin/python3


import random
from collections import Counter

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
		self.bad=False

	def add_peer(self, idx):
		if self.idx!=idx and not(idx in self.connected):
			if len(self.connected) < max_hosts and (len(self.peers[idx].connected) < max_hosts):
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

	def get_info(self):
		# that host will ask all the other the value
#TODO write an object with time, so it picks the most recent value
		l=[]
		for i in self.connected:
			if self.peers[i].info != None:
				l.append(self.peers[i].info)
		return l

	def choose_info(self): #choose an info amongst all its peer to get the most common 
		if not self.bad:
			c=Counter(self.get_info())
			if len(c)>0:
				self.info=c.most_common()[0][0] 
		else:
			self.info=0-random.randrange(0,100) # < 0 so i can spot it



class Peers(): 
	def __init__(self): 
		self.peers = []
		self.bad_guys_ratio=0

	def add_random(self): # add a host and connect to a random one
		idx=len(self.peers)
		p=Peer(idx, self.peers)	
		self.peers.append(p)
		if len(self.peers)>1:
			while True:
				if p.add_peer(random.choice(self.peers).idx):
					break

		if random.random()<self.bad_guys_ratio:
			p.bad=True

		return p

	def count_bad_guys(self):
		return len([k for k in self.peers if k.bad==True])

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
			print("avg size = %0.5f" % a)
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
				i.choose_info()
			p=self.check_info(info)
			print("percentage is %0.5f" % (p*100))

def experiment():
	print("initializing")
	a=Peers()
	print("setting percentage of bad guys")
	a.bad_guys_ratio=0.01 # 1% of bad guys screw the network
	print("adding randoms")
	a.add_randoms(10000)
	print("stabilizing")
	a.check_till_stable()
	print("removing randoms")
	a.disconnect_randoms(300)
	print("stabilizing")
	a.check_till_stable() 
	print("passing info 1")
	a.pass_info(1)
	print("passing info 2")
	a.pass_info(2)
	print("passing info 1")
	a.pass_info(1)
	return a
