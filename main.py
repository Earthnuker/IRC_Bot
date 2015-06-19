import socket
import getpass
import select
import threading
import shelve
import random
import sys
import os
import time
import datetime
import hack
import string
import codecs
from multiprocessing.pool import ThreadPool
from multiprocessing import TimeoutError
def int2base(x, base):
	digs = string.digits + string.ascii_lowercase
	if x < 0:
		sign = -1
	elif x == 0:
		return digs[0]
	else:
		sign = 1
	x *= sign
	digits = []
	while x:
		digits.append(digs[x % base])
		x //= base
	if sign < 0:
		digits.append('-')
	digits.reverse()
	return ''.join(digits)

def recvall(sock):
	data=""
	while True:
		chunk=str(sock.recv(4096),"utf-8")
		data+=chunk
		if data.endswith("\n"):
			return data.splitlines()

def send(sock,data,verbose=True):
	if verbose:print(">",data)
	return sock.send(bytes(data,"utf-8")+b"\n")

class Commands(object):
	def __init__(self,bot):
		self.pool=ThreadPool(processes=1)
		self.threads=dict()
		self.commands=[cmd for cmd in dir(self) if cmd.startswith("cmd_")]
		self.bot=bot
		self.admins=[self.bot.owner]
		modules=set(["math","cmath","sympy","numpy","scipy","datetime","time","random"])
		self.safe_builtins=set([len,range,dir,chr,ord])
		self.calc_mods={"__builtins__":{func.__name__:func for func in self.safe_builtins}}
		for mod in modules:
			try:
				self.calc_mods[mod]=__import__(mod)
			except ImportError as e:
				print("Unable to load module {}:{}".format(mod,e))
				if mod in self.modules:
					modules.remove(mod)
		self.modules=modules
	"""
	def _privileged(func):
		def protected(*args,**kwargs):
			self=args[0]
			if self.bot.lastmsg['src'].split("@")[0].split("!")[0] not in self.admins:
				return 
			else:
				return func(*args,**kwargs)
		return protected
	
	@_privileged
	def terminate(self,msg=None):
		self.bot.terminate(msg)
	""" # Does not work D:
	
	def cmd_trigger(self,trigger):
		if len(trigger)>1:
			return "Trigger must be a single character"
		else:
			self.bot.trigger=trigger
			return "Trigger set to {}".format(trigger)
	
	def cmd_baseconv(self,b_from,b_to,n):
		b_from=b_from.lower()
		b_to=b_to.lower()
		bd={'hex':16,'oct':8,'bin':2,'dec':10}
		if b_from in bd:
			b_from=bd[b_from]
		else:
			b_from=int(b_from)
		if b_to in bd:
			b_to=bd[b_to]
		else:
			b_to=int(b_to)
		result=int2base(int(n,b_from),b_to)
		return "{} (Base {}) = {} (Base {})".format(n,b_from,result,b_to)
	def cmd_stopcalc(self):
		self.pool.terminate()
		self.pool=ThreadPool(processes=1)
		self.threads=dict()
		return "All Computations terminated"
	def cmd_calc(self,*expr):
		expr=" ".join(expr)
		for badword in ["__builtins__","__import__","__call__","__class__","__getattribute__","__getattr__","__dict__"]:
			if expr.find(badword)!=-1:
				return "foudn blacklisted expression: {}".format(badword)
		def runme():
			t_s=time.time()
			ret=eval(expr,self.calc_mods,self.calc_mods)
			d_t=datetime.timedelta(seconds=time.time()-t_s)
			return "{} <{}>".format(ret,d_t)
		self.threads[(time.time(),expr)]=self.pool.apply_async(runme,())
		new_threas=dict()
		for (started,expr),thread in self.threads.items():
			if thread:
				new_threas[(started,expr)]=thread
		self.threads=new_threas
		for (started,expr),thread in self.threads.items():
			if (time.time()-started)>60:
				self.threads[(started,expr)]=None
				return "{} Timed out".format(expr)
			try:
				result=thread.get(1)
			except TimeoutError:
				result=None
			if result:
				self.threads[(started,expr)]=None
				return "{} => {}".format(expr,result)
		return
	
	def cmd_lsmod(self):
		return "Available modules: "+",".join(self.modules)
		
	def cmd_dice(self,sides=6,num=1):
		if int(num)>100:
			return "Too many dice"
		return "{}d{}".format(num,sides)+"=["+",".join(map(str,(random.randint(1,int(sides)) for _ in range(int(num)))))+"]"
	
	def cmd_fortune(self):
		cd,dirs,files=random.choice(list(os.walk("fortunes")))
		unrot13=cd.endswith("off")
		fortune_file=os.path.join(cd,random.choice(files))
		with open(fortune_file) as ff:
			data=ff.read()
		if data:
			fortune=False
			while not (fortune and len(fortune)<500):
				fortune=random.choice(data.split("%")).strip().replace("\n"," ")
		if unrot13:
			fortune=codecs.decode(fortune,"rot13")
		return fortune+" [{}]".format(fortune_file)
		
	def cmd_help(self,command=None):
		if not command:
			return "available commands: "+",".join(map(lambda x:x[4:],self.commands))
		try:
			cmd=self.__getattribute__(command)
			if cmd.__doc__:
				return cmd.__doc__
		except Exception as e:
			return str(e)
	
	def cmd_greet(self,name=None):
		if name:
			return "Hello {}".format(name)
		return "Hello {}".format(self.bot.lastmsg['src'].split("@")[0].split("!")[0])
	
	def cmd_hollywood_hacking(self):
		return hack.run()
		
	def cmd_bofh(self):
		bofh_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		bofh_socket.connect(("towel.blinkenlights.nl",666))
		return recvall(bofh_socket)[-1]
	
	def __call__(self,item,args):
		try:
			return self.__getattribute__("cmd_"+item)(*args)
		except Exception as e:
			return str(e)
	
class IRCBot(object):

	def __init__(self):
		self.nicklist={}
		self.trigger="$"
		self.server="irc.freenode.net"
		self.port=6667
		#self.channels=["#tuug"]
		self.channels=['#earthnuker_bot_test']
		self.nick="EN_bot_test"
		self.owner="Earthnuker"
		self.password=getpass.getpass("Password:")
		self.execute=Commands(self)
		#self.db=shelve.open("log.db","c",writeback=True)
	
	def run(self):
		initial_commands=[
			"USER {} {} {} {}".format(self.nick,self.nick,self.nick,self.owner),
			"NICK {}".format(self.nick),
			"PRIVMSG NickServ :identify {} {}".format(self.owner,self.password),
		]+["JOIN {}".format(channel) for channel in self.channels]
		self.irc_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.irc_socket.connect((self.server,self.port))
		self.irc_server=self.irc_socket.getpeername()
		print("Connected to {}:{}".format(*self.irc_server))
		for cmd in initial_commands:
			if self.password in cmd:
				send(self.irc_socket,cmd,False)
			else:
				send(self.irc_socket,cmd)
		while 1:
			for message in recvall(self.irc_socket):
				self.process(message)
	
	def terminate(self,msg):
		if msg:
			send(self.irc_socket,"QUIT {}".format(msg))
		else:
			send(self.irc_socket,"QUIT Terminating")
		self.irc_socket.close()
		#self.db.close()
		exit(0)
		
	def process(self,message):
		if message.startswith(":"):
			src,type,to,*cont=message[1:].split()
		else:
			src=None
			to=None
			type,*cont=message.split()
		cont=" ".join(cont)[1:]
		if type!="PING":
			print(message)
		if type=="PING":
			send(self.irc_socket,"PONG {}".format(cont),False)
		if type=="PRIVMSG":
			print(to)
			if to in self.channels+[self.nick]:
				if cont[0]==self.trigger:
					args=cont.split(" ")
					command=args[0][len(self.trigger):]
					self.lastmsg={"src":src,"type":type,"to":to,"cont":cont}
					ret=self.execute(command,args[1:])
					if ret:
						if to==self.nick:
							to=src.split("!")[0]
						send(self.irc_socket,"PRIVMSG {} :{}".format(to,ret))
			if cont[0]!=self.trigger:
				pass
				#if src in self.db:
				#	self.db[src].append(cont)
				#	print(src)
				#else:
				#	self.db[src]=[]
		if type=="353":
			channel=cont.split(" ")[1].strip()
			self.nicklist[channel]=cont.split(" ")[2:]
			self.nicklist[channel][0]=self.nicklist[channel][0][1:]
			print(self.nicklist)
Bot=IRCBot()
Bot.run()