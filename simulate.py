#!/usr/bin/python3


import random
from collections import Counter

class Block:
	def __init__(self):
		self.data=None # will be a value
		self.owner=None
		self.hash_ok=True # by default, the hash is ok. will be wrong if guy is bad
		self.previous_block_data=None

verbose=3 # 1: experiment, 2: Peers, 3: Peer
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
		self.blockchain=[] # array of Block

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

	def get_blockchain(self):
		global verbose
		bb=None # biggest blockchain found
		max_len=-1
		for i in self.connected:
			ob=self.peers[i].blockchain
			if len(ob) > len(self.blockchain):
				ok=True
				for j in ob[len(self.blockchain):]: # for each new block
					if not j.hash_ok:
						ok=False
						break 
				if verbose>=5:
					if ok:
						print("Other's blockchain is right")
					else:
						print("Other's blockchain is wrong")
				if ok:
					if len(ob)>max_len:
						max_len=len(ob) 
					bb=ob

		if bb != None:
			if verbose>=5:
				print("Synchronizing")

			# we check from my item going back in time where we do match
			i=len(self.blockchain)-1
			diff=True
			while (i > 0) and diff:
				diff=self.blockchain[i].data==bb[i].data # of course i should compare some checksum here 
				if diff:
					i=i-1

			self.blockchain=self.blockchain[0:i]

			for j in bb[i:]: # for each new block
				self.blockchain.append(j) 

	def mine_block(self, rg):
# data = last data mined in the blockchain + random value from 0 to 'rg'
		b=Block()
		if self.blockchain==[]:
			b.data=0 # good quest, who wins ? the oldest ? how to prove you're owning the oldest ?
		else:
			b.data=random.randrange(1, rg) 
			b.previous_block_data=self.blockchain[-1].data
		b.has_ok=self.bad
		b.owner=self.idx
		self.blockchain.append(b)

	def get_blockchain_data(self):
		return ', '.join([("%d" % a.data) for a in self.blockchain])

	def get_blockchain_owner(self):
		return ', '.join([("%d" % a.owner) for a in self.blockchain])

	def get_sum(self):
		return sum([a.data for a in self.blockchain])

class Peers(): 
	def __init__(self): 
		self.peers = []
		self.bad_guys_ratio=0
		self.books=[]

	def add_random(self): # add a host and connect to a random one
		idx=len(self.peers)
		p=Peer(idx, self.peers)	
		self.peers.append(p)
		if len(self.peers)>1:
			while True:
				if p.add_peer(random.choice(self.peers).idx):
					break

		if random.random()<self.bad_guys_ratio:
			print("%d is bad" % p.idx)
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

	def random_peer_mine_block(self):
		p=random.choice(self.peers)
		p.mine_block(10)
		return p

	def check_blockchain(self):
		for i in self.peers:
			i.get_blockchain()

	def get_avg_blockchain_length(self):
		a=sum([len(a.blockchain) for a in self.peers])
		b=len(self.peers)
		return a/b

	def check_blockchain_till_stable(self):
		avg_len=-2
		old_avg_len=-1
		while avg_len != old_avg_len:
			self.check_blockchain()
			old_avg_len=avg_len
			avg_len=self.get_avg_blockchain_length()
		return avg_len

	def random_mining(self, count_block_mined_simulatenously, min_ticks, max_ticks, count_blocks):
		ticks=0
		for i in range(0, count_blocks):
			if ticks<=0:
				for j in range(0, count_block_mined_simulatenously):
					p=self.random_peer_mine_block()
				if verbose>=2:
					print("%d mined" % p.idx) 
				ticks=random.randrange(min_ticks, max_ticks)
			ticks=ticks-1
			self.check_blockchain()
			print("avg length = %0.2f" % self.get_avg_blockchain_length() )



def experiment():
	print("initializing peers")
	a=Peers()
	print("setting percentage of bad guys")
	a.bad_guys_ratio=0.01 # 1% of bad guys screw the network
	print("adding randoms")
	a.add_randoms(10000)
	print("stabilizing")
	a.check_till_stable()
	print("removing randoms")
	a.disconnect_randoms(int(len(a.peers)/10))
	print("stabilizing")
	a.check_till_stable() 
	print("living blockchain for 1000 turns, 1 block mined every 10/15 turnes")
	a.random_mining(5, 1, 5, 1000) # PoW
	# need to code PoS, so each node knows which node will be picked up... that's another story clearly

	return a 
