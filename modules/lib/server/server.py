# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
from tools import jsonconfig,useful,info
import wifi
import uasyncio
import time

class ServerConfig(jsonconfig.JsonConfig):
	""" Servers configuration """
	def __init__(self):
		jsonconfig.JsonConfig.__init__(self)
		self.ntp = True
		self.ftp = True
		self.http = True
		self.telnet = True
		self.wanip = True
		self.offsettime = 1
		self.dst = True
		self.currentTime = 0
		self.notify = True
		self.serverPostponed = 10

class ServerContext:
	""" Context to initialize the servers """
	def __init__(self, loop=None, pageLoader=None, preload=False, httpPort=80):
		from server.timesetting import setTime
		self.loop          = loop
		self.pageLoader    = pageLoader
		self.preload       = preload
		self.httpPort      = httpPort
		self.serverStarted = False
		self.notifier      = None
		self.getWanIpAsync = None
		self.wanIp = None
		self.config        = ServerConfig()
		self.setDate = None
		self.onePerDay = None
		self.flushed = False
		
		if self.config.load() == False:
			self.config.save()
		self.serverPostponed = self.config.serverPostponed
		setTime(self.config.currentTime)

class Server:
	""" Class used to manage the servers """
	suspended = [False]
	slowSpeed = [None]
	tasks = {}
	context = None

	@staticmethod
	def suspend():
		""" Suspend the asyncio task of servers """
		Server.suspended[0] = True

	@staticmethod
	def resume():
		""" Resume the asyncio task of servers """
		Server.suspended[0] = False

	@staticmethod
	async def waitResume(duration=None):
		""" Wait the resume of task servers """
		if duration != None:
			Server.tasks[id(uasyncio.current_task())] = True
			await uasyncio.sleep(duration)
		if Server.suspended[0]:
			Server.tasks[id(uasyncio.current_task())] = True
			while Server.suspended[0]:
				await uasyncio.sleep(1)
		Server.tasks[id(uasyncio.current_task())] = False

	@staticmethod
	def isSlow():
		""" Indicates that task other than server must be slower """
		if Server.slowSpeed[0] == None:
			return False
		elif time.time() > Server.slowSpeed[0]:
			Server.slowSpeed[0] = None
			return False
		else:
			return True

	@staticmethod
	def slowDown(duration=10):
		""" Set the state slow for a specified duration """
		Server.slowSpeed[0] = time.time() + duration

	@staticmethod
	def isAllWaiting():
		""" Check if all task resumed """
		result = True
		for key, value in Server.tasks.items():
			if value == False:
				result = False
		return result

	@staticmethod
	async def waitAllSuspended():
		""" Wait all servers suspended """
		for i in range(150):
			if Server.isAllWaiting() == True:
				break
			else:
				if i % 30 == 0:
					print("Wait all servers suspended...")
				await uasyncio.sleep(0.1)
				useful.WatchDog.feed()

	@staticmethod
	def init(loop=None, pageLoader=None, preload=False, httpPort=80):
		""" Init servers
		loop : asyncio loop
		pageLoader : callback to load html page
		preload : True force the load of page at the start, 
		False the load of page is done a the first http connection (Takes time on first connection) """
		Server.context = ServerContext(loop, pageLoader, preload, httpPort)
		useful.logError(useful.sysinfo(display=False))
		build = info.build.replace("/","-")
		build = build.replace("  ","_")
		build = build.replace(":","-")
		useful.logError("PyCam version '%s'"%build)

		from server.periodic import periodicTask
		loop.create_task(periodicTask())

	@staticmethod
	async def synchronizeWanIp(forced):
		""" Synchronize wan ip """
		# If wan ip synchronization enabled
		if Server.context.config.wanip:
			if wifi.Wifi.isWanAvailable():
				useful.logError("Synchronize Wan ip")
				# Wan ip not yet get
				if Server.context.getWanIpAsync is None:
					from server.wanip import getWanIpAsync
					Server.context.getWanIpAsync = getWanIpAsync

				# Get wan ip 
				newWanIp = await Server.context.getWanIpAsync()

				# If wan ip get
				if newWanIp is not None:
					# If wan ip must be notified
					if (Server.context.wanIp != newWanIp or forced):
						await Server.context.notifier.notify("Lan Ip %s, Wan Ip %s, %s"%(wifi.Station.getInfo()[0],newWanIp, useful.uptime()))
					Server.context.wanIp = newWanIp
					wifi.Wifi.connectWan()
				else:
					useful.logError("Cannot get wan ip")
					wifi.Wifi.disconnectWan()

	@staticmethod
	async def synchronizeTime():
		""" Synchronize time """
		# If ntp synchronization enabled
		if Server.context.config.ntp:
			# If the wan is present
			if wifi.Wifi.isWanAvailable():
				useful.logError("Synchronize time")

				# If synchronisation not yet done
				if Server.context.setDate == None:
					from server.timesetting import setDate
					Server.context.setDate = setDate

				updated = False
				# Try many time
				for i in range(3):
					# Keep old date
					oldTime = time.time()

					# Read date from ntp server
					currentTime = Server.context.setDate(Server.context.config.offsettime, dst=Server.context.config.dst, display=False)

					# If date get
					if currentTime > 0:
						# Save new date
						Server.context.config.currentTime = int(currentTime)
						Server.context.config.save()

						# If clock changed
						if abs(oldTime - currentTime) > 1:
							# Log difference
							useful.logError("Time synchronized delta=%ds"%(currentTime-oldTime))
						updated = True
						break
					else:
						await uasyncio.sleep(1)
				if updated:
					wifi.Wifi.connectWan()
				else:
					wifi.Wifi.disconnectWan()

	@staticmethod
	def isOnePerDay():
		""" Indicates if the action must be done on per day """
		date = useful.dateToBytes()[:14]
		if Server.context.onePerDay is None or (date[-2:] == b"12" and date != Server.context.onePerDay):
			Server.context.onePerDay = date
			return True
		return False

	@staticmethod
	async def startServer():
		""" Start all servers """
		# If server not started
		if Server.context.serverStarted == False:
			# If wifi available
			if wifi.Wifi.isLanConnected():
				Server.context.serverStarted = True
				config = Server.context.config

				# Add notifier if no notifier registered
				if Server.context.notifier.isEmpty():
					from server.pushover import notifyMessage
					Server.context.notifier.add(notifyMessage)

				# If telnet activated
				if config.telnet:
					# Load and start telnet
					import server.telnet
					server.telnet.start()

				# If ftp activated
				if config.ftp:
					# Load and start ftp server
					import server.ftpserver
					server.ftpserver.start(loop=Server.context.loop, preload=Server.context.preload)

				# If http activated
				if config.http:
					# Load and start http server
					import server.httpserver
					server.httpserver.start(loop=Server.context.loop, loader=Server.context.pageLoader, preload=Server.context.preload, port=Server.context.httpPort, name="httpServer")

					# If camera present
					if useful.iscamera():
						# Load and start streaming http server
						server.httpserver.start(loop=Server.context.loop, loader=Server.context.pageLoader, preload=Server.context.preload, port=Server.context.httpPort +1, name="StreamingServer")

				from server.presence import detectPresence
				Server.context.loop.create_task(detectPresence())

	@staticmethod
	async def manage(pollingId):
		""" Manage the network and server """
		if Server.context.serverPostponed == 0:
			await Server.startServer()

			if pollingId %179 == 0:
				await wifi.Wifi.manage()

			if pollingId %181 == 0 and Server.context.flushed == False:
				if wifi.Wifi.isWanAvailable():
					await Server.synchronizeTime()
					await Server.context.notifier.flush()
					if wifi.Wifi.isWanConnected():
						Server.context.flushed = True

			if pollingId % 3607 == 0:
				await Server.synchronizeTime()

			forced =  Server.isOnePerDay()
			if pollingId % 3593 == 0 or forced:
				await Server.synchronizeWanIp(forced)

		else:
			Server.context.serverPostponed -= 1
   
			if Server.context.serverPostponed == 0:
				from server.notifier import Notifier
				Server.context.notifier = Notifier

				await wifi.Wifi.manage()
				if wifi.Wifi.isWanAvailable():
					await Server.synchronizeTime()
					await Server.context.notifier.flush()
					if wifi.Wifi.isWanConnected():
						Server.context.flushed = True
  
