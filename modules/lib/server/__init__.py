# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class for servers FTP, HTTP, Telnet.
Class to dialog with NTP, PushOver. 
Class to manage session, user password, stream."""
from server import *
from server.sessions import *
from server.user import *
from server.pushover import *
from server.wanip import *
from server.ping import *
from server.dnsclient import *
from server.timesetting import *
from server.wanip import *
from server.periodic import *
from tools import jsonconfig,useful
import uasyncio
import wifi
import time

class ServerConfig(jsonconfig.JsonConfig):
	""" Servers configuration """
	def __init__(self):
		jsonconfig.JsonConfig.__init__(self)
		self.ntp = True
		self.ftp = True
		self.http = True
		self.telnet = True
		self.offsettime = 1
		self.dst = True
		self.currentTime = 0
		self.notify = True

def start(loop=None, pageLoader=None, preload=False, withoutServer=False, httpPort=80):
	""" Start all servers
	loop : asyncio loop
	pageLoader : callback to load html page
	preload : True force the load of page at the start, 
	False the load of page is done a the first http connection (Takes time on first connection) """
	useful.logError("%s Start %s"%('-'*10,'-'*10), display=False)

	# Add notifier if no notifier registered
	if useful.getNotifier() == []:
		useful.addNotifier(notifyMessage)

	# If wifi started
	if wifi.start():
		from server import ServerConfig
		config = ServerConfig()
		if config.load() == False:
			config.save()
		
		# restore saved time
		setTime(config.currentTime)

		# If ntp synchronisation activated
		if config.ntp:
			# Load and start ntp synchronisation
			loop.create_task(periodicTask())

		# If telnet activated
		if config.telnet and withoutServer == False:
			# Load and start telnet
			import server.telnet
			server.telnet.start()

		# If ftp activated
		if config.ftp and withoutServer == False:
			# Load and start ftp server
			import server.ftpserver
			server.ftpserver.start(loop=loop, preload=preload)

		# If http activated
		if config.http and withoutServer == False:
			# Load and start http server
			import server.httpserver
			server.httpserver.start(loop=loop, loader=pageLoader, preload=preload, port=httpPort, name="httpServer")

			# If camera present
			if useful.iscamera():
				# Load and start streaming http server
				server.httpserver.start(loop=loop, loader=pageLoader, preload=preload, port=httpPort +1, name="StreamingServer")
	
	# Display system informations
	useful.sysinfo()


_suspended = [False]
_tasks = {}
def suspend():
	""" Suspend the asyncio task of servers """
	_suspended[0] = True

def resume():
	""" Resume the asyncio task of servers """
	_suspended[0] = False

async def waitResume(duration=None):
	""" Wait the resume of task servers """
	if duration != None:
		_tasks[id(uasyncio.current_task())] = True
		await uasyncio.sleep(duration)
	if _suspended[0]:
		_tasks[id(uasyncio.current_task())] = True
		while _suspended[0]:
			await uasyncio.sleep(1)
	_tasks[id(uasyncio.current_task())] = False

def isAllWaiting():
	""" Check if all task resumed """
	result = True
	for key, value in _tasks.items():
		if value == False:
			result = False
	return result

async def waitAllSuspended():
	""" Wait all servers suspended """
	for i in range(150):
		if server.isAllWaiting() == True:
			break
		else:
			if i % 30 == 0:
				print("Wait all servers suspended...")
			await uasyncio.sleep(0.1)

