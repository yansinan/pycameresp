# Distributed under MIT License
# Copyright (c) 2021 Remi BERTHOLET
""" Class defining a minimalist shell, directly executable on the board. 
We modify directories, list, delete, move files, edit files ...
The commands are :
- cd      : change directory
- pwd     : current directory
- cat     : display the content of file
- mkdir   : create directory
- mv      : move file
- rmdir   : remove directory
- cp      : copy file
- rm      : remove file
- ls      : list file
- date    : get the system date or synchronize with Ntp
- setdate : set date and time
- df      : display free disk space
- find    : find a file
- run     : run a script
- edit    : edit a text file
- exit    : exit of shell
- gc      : garbage collection
- grep    : grep text in many files
- ping    : ping host
- mount   : mount sd card
- umount  : umount sd card
- meminfo : memory informations
- flashinfo: flash informations
- sysinfo : system informations
- deepsleep: deepsleep of board
- reboot  : reboot board
- help    : list all command available
- man     : manual of one command
"""
import sys
sys.path.append("lib")
import os
import uos
import machine
try:
	from tools import useful
except:
	import useful

def cd(directory = "/"):
	""" Change directory """
	try:
		uos.chdir(directory)
	except:
		print("No such file or directory '%s'"%directory)

def pwd():
	""" Display the current directory """
	print("%s"%uos.getcwd())

def mkdir(directory, recursive=False, quiet=False):
	""" Make directory """
	try:
		if quiet == False:
			print("mkdir '%s'"%directory)
		useful.makedir(directory, recursive)
	except:
		print("Cannot mkdir '%s'"%directory)

def removedir(directory, force=False, quiet=False, simulate=False):
	""" Remove directory """
	try:
		if useful.exists(directory+"/.DS_Store"):
			rmfile(directory+"/.DS_Store", quiet, force, simulate)
		if (useful.ismicropython() or force) and simulate == False:
			uos.rmdir(directory)
		if quiet == False:
			print("rmdir '%s'"%(directory))
	except:
		print("rmdir '%s' not removed"%(directory))

def rmdir(directory, recursive=False, force=False, quiet=False, simulate=False):
	""" Remove directory """
	if recursive == False:
		removedir(directory, force=force, quiet=quiet, simulate=simulate)
	else:
		directories = [directory]
		d = directory
		while 1:
			parts = useful.split(d)
			if parts[1] == "" or parts[0] == "":
				break
			directories.append(parts[0])
			d = parts[0]
		if "/" in directories:
			directories.remove("/")
		if useful.SdCard.getMountpoint() in directories:
			directories.remove(useful.SdCard.getMountpoint())
		for d in directories:
			if useful.exists(d) and d != ".":
				removedir(d, force=force, quiet=quiet, simulate=simulate)

def mv(source, destination):
	""" Move or rename file """
	try:
		uos.rename(source,destination)
	except:
		print("Cannot mv '%s'->'%s'"%(source,destination))

def copyfile(src,dst,quiet):
	""" Copy file """
	dst = dst.replace("//","/")
	dst = dst.replace("//","/")
	dstdir, dstfile = useful.split(dst)
	try:
		if not useful.exists(dstdir):
			if dstdir != "." and dstdir != "":
				mkdir(dstdir, recursive=True, quiet=quiet)
		src_file = open(src, 'rb')
		dst_file = open(dst, 'wb')
		if quiet == False:
			print("cp '%s' -> '%s'"%(src,dst))
		while True:
			buf = src_file.read(256)
			if len(buf) > 0:
				dst_file.write(buf)
			if len(buf) < 256:
				break
		src_file.close()
		dst_file.close()
	except:
		print("Cannot cp '%s' -> '%s'"%(src, dst))

def cp(source, destination, recursive=False, quiet=False):
	""" Copy file command """
	filenames   = []
	directories = []

	if useful.isfile(source):
		copyfile(source,destination,quiet)
	else:
		if useful.isdir(source):
			path = source
			pattern = "*"
		else:
			path, pattern = useful.split(source)
				
		directories, filenames = useful.scandir(path, pattern, recursive)

		for src in filenames:
			dst = destination + "/" + src[len(path):]
			copyfile(src,dst,quiet)

def rmfile(filename, quiet=False, force=False, simulate=False):
	""" Remove file """
	try:
		if (useful.ismicropython() or force) and simulate == False:
			uos.remove(filename)
		if quiet == False:
			print("rm '%s'"%(filename))
	except:
		print("rm '%s' not removed"%(filename))

def rm(file, recursive=False, quiet=False, force=False, simulate=False):
	""" Remove file command """
	filenames   = []
	directories = []
	
	if useful.isfile(file):
		path = file
		rmfile(file, force=force, quiet=quiet, simulate=simulate)
	else:
		if useful.isdir(file):
			if recursive:
				directories.append(file)
				path = file
				pattern = "*"
			else:
				path = None
				pattern = None
		else:
			path, pattern = useful.split(file)

		if path == None:
			print("Cannot rm '%s'"%file)
		else:
			dirs, filenames = useful.scandir(path, pattern, recursive)
			directories += dirs
					
			for filename in filenames:
				rmfile(filename, force=force, quiet=quiet, simulate=simulate)
		
			if recursive:
				directories.sort()
				directories.reverse()

				for directory in directories:
					rmdir(directory, recursive=recursive, force=force, quiet=quiet, simulate=simulate)

class LsDisplayer:
	""" Ls displayer class """
	def __init__(self, path, showdir, long):
		""" Constructor """
		self.height, self.width = useful.getScreenSize()
		self.count = 1
		self.long = long
		self.path = path
		self.showdir = showdir

	def purgePath(self, path):
		""" Purge the path for the display """
		if path != "/":
			path = path.replace(self.path,"")
		if len(path) >= 2 and path[:2] == "./":
			path = path[2:]
		path = path.lstrip("/")
		return path

	def show(self, path):
		""" Show the information of a file or directory """
		fileinfo = useful.fileinfo(path)
		date_ = fileinfo[8]
		size = fileinfo[6]

		# If directory
		if fileinfo[0] & 0x4000 == 0x4000:
			if self.showdir:
				if self.long:
					message = "%s %s [%s]"%(useful.dateToString(date_)," "*7,self.purgePath(path))
				else:
					message = "[%s]"%self.purgePath(path)
				self.count = printPart(message, self.width, self.height, self.count)
		else:
			if self.long:
				fileinfo = useful.fileinfo(path)
				date_ = fileinfo[8]
				size = fileinfo[6]
				message = "%s %s %s"%(useful.dateToString(date_),useful.sizeToString(size),self.purgePath(path))
			else:
				message = self.purgePath(path)
			self.count = printPart(message, self.width, self.height, self.count)

def ls(file="", recursive=False, long=False):
	""" List command """
	if useful.isfile(file):
		LsDisplayer("", False, long).show(file)
	elif file == "":
		useful.scandir(uos.getcwd(), "*", recursive, LsDisplayer(uos.getcwd(), True, long))
	elif useful.isdir(file):
		useful.scandir(file, "*", recursive, LsDisplayer(file, True, long))
	else:
		path, pattern = useful.split(file)
		useful.scandir(path, pattern, recursive, LsDisplayer(path, False, long))

def find(file):
	""" Find a file in directories """
	path, pattern = useful.split(file)
	directories, filenames = useful.scandir(path, pattern, True)
	for filename in filenames:
		print(filename)

def printPart(message, width, height, count):
	""" Print a part of text """
	if count != None and count >= height:
		print(message,end="")
		key = useful.getch()
		count = 1
		if key in ["x","X","q","Q","\x1B"]:
			return None
		print("\n", end="")
	else:
		if count == None:
			count = 1
		else:
			count += 1
		print(message)
	return count

def grep(file, text, recursive=False, ignorecase=False, regexp=False):
	""" Grep command """
	from re import search
	def __search(text, content, ignorecase, regexp):
		if ignorecase:
			content  = content.lower()
			text = text.lower()
		if regexp:
			if search(text, content):
				return True
		else:
			if content.find(text) != -1:
				return True
		return False

	def __grep(text, filename, ignorecase, regexp, width, height, count):
		lineNumber = 1
		with open(filename,"r", encoding="latin-1") as f:
			while 1:
				line = f.readline()
				if line:
					if __search(text, line, ignorecase, regexp):
						line = line.replace("\t","    ")
						message = "%s:%d:%s"%(filename, lineNumber, line)
						message = message.rstrip()[:width]
						count = printPart(message, width, height, count)
						if count == None:
							print("")
							return None
					lineNumber += 1
				else:
					break
		return count

	if useful.isfile(file):
		filenames = [file]
	else:
		path, pattern = useful.split(file)
		directories, filenames = useful.scandir(path, pattern, recursive)

	height, width = useful.getScreenSize()
	count = 1
	for filename in filenames:
		count = __grep(text, filename, ignorecase, regexp, width, height, count)
		if count == None:
			break

def ping(host):
	""" Ping host """
	from server.ping import ping as ping_
	ping_(host, count=4, timeout=1)

def ip2host(ipaddress):
	""" Convert ip to hostname """
	import wifi
	_, _, _, dns = wifi.Station.getInfo()
	from server.dnsclient import resolveHostname
	print(resolveHostname(dns, ipaddress))

def host2ip(hostname):
	""" Convert hostname to ip """
	import wifi
	_, _, _, dns = wifi.Station.getInfo()
	from server.dnsclient import resolveIpAddress
	print(resolveIpAddress(dns, hostname))

def mountsd(mountpoint="/sd"):
	""" Mount command """
	try:
		uos.mount(machine.SDCard(), mountpoint)
		print("Sd mounted on '%s'"%mountpoint)
	except:
		print("Cannot mount sd on '%s'"%mountpoint)

def umountsd(mountpoint="/sd"):
	""" Umount command """
	try:
		uos.umount(mountpoint)
		print("Sd umounted from '%s'"%mountpoint)
	except:
		print("Cannot umount sd from '%s'"%mountpoint)

def date(update=False, offsetUTC=+1, noDst=False):
	""" Get or set date """
	from server.timesetting import setDate
	if update:
		if noDst:
			dst = False
		else:
			dst = True
		setDate(offsetUTC, dst)
	print(useful.dateToString())
	del sys.modules["server.timesetting"]

def setdate(datetime=""):
	""" Set date and time """
	import re
	date_=re.compile("[/: ]")
	failed = False
	try:
		spls = date_.split(datetime)

		lst = []
		if len(spls) > 1:
			for spl in spls:
				if len(spl) > 0:
					try:
						r = spl.lstrip("0")
						if len(r) == 0:
							lst.append(0)
						else:
							lst.append(eval(r))
					except:
						failed = True
						break
		if len(lst) == 6:
			# pylint: disable=unbalanced-tuple-unpacking
			year,month,day,hour,minute,second = lst
			machine.RTC().datetime((year, month, day, 0, hour, minute, second, 0))
		else:
			failed = True
	except Exception as err:
		failed = True
		useful.exception(err)

	if failed == True:
		print('Expected format "YYYY/MM/DD hh:mm:ss"')

def reboot():
	""" Reboot command """
	useful.reboot("Reboot device")

def deepsleep():
	""" Deep sleep command """
	machine.deepsleep()

editClass = None
def edit(file):
	""" Edit command """
	global editClass
	if editClass == None:
		try:
			from shell.editor import Editor
		except:
			from editor import Editor
		editClass = Editor
	editClass(file)

def cat(file):
	""" Cat command """
	try:
		f = open(file, "r")
		height, width = useful.getScreenSize()
		count = 1
		while 1:
			line = f.readline()
			if not line:
				break
			message = line.replace("\t","    ").rstrip()[:width]
			count = printPart(message, width, height, count)
			if count == None:
				break
		f.close()
	except:
		print("Cannot cat '%s'"%(file))

def df(mountpoint = "/"):
	""" Display free disk space """
	status = uos.statvfs(mountpoint)
	freeSize  = status[0]*status[3]
	totalSize = status[1]*status[2]
	print("Filesystem     Free   Capacity   Used")
	print("%-10s %-10s %-10s %-3.2f%%"%(mountpoint, useful.sizeToString(freeSize,8),useful.sizeToString(totalSize,), totalSize/freeSize))

def gc():
	""" Garbage collector command """
	from gc import collect
	collect()

def uptime():
	""" Tell how long the system has been running """
	print(useful.uptime())

def man(command):
	""" Man command """
	print(manOne(command))

def manOne(commandName):
	""" Manual of one command """
	try:
		commandName, commandFunction, commandParams, commandFlags = getCommand(commandName)
		text = "  " + commandName + " "
		for param in commandParams:
			text += param + " "
		text += "\n"
		for flag,flagName,val in commandFlags:
			text += "    %s : %s\n"%(flag,flagName)
		result = text[:-1]
	except:
		result = "Unknown command '%s'"%commandName
	return result

# pylint: disable=redefined-builtin
def help():
	""" Help command """
	height, width = useful.getScreenSize()
	count = 1
	cmds = list(shellCommands.keys())
	cmds.sort()
	for command in cmds:
		lines = manOne(command)
		lines = "-"*30+"\n" + lines
		for line in lines.split("\n"):
			count = printPart(line, width, height, count)
			if count == None:
				return 

shell_exited = False
def exit():
	""" Exit shell command """
	global shell_exited
	shell_exited = True

def parseCommandLine(commandLine):
	""" Parse command line """
	commands = []
	args = []
	quote = False
	arg = ""
	for char in commandLine:
		if char == '"' or char == "'":
			if quote:
				args.append(arg)
				arg = ""
				quote = False
			else:
				quote = True
		elif char == " ":
			if quote == True:
				arg += char
			else:
				args.append(arg)
				arg = ""
		elif char == ";":
			if quote == True:
				arg += char
			else:
				if len(arg) > 0:
					args.append(arg)
				commands.append(args)
				arg = ""
				args = []
		else:
			arg += char
	if len(arg) > 0:
		args.append(arg)
	if len(args) > 0:
		commands.append(args)

	for command in commands:
		execCommand(command)

def cls():
	""" Clear screen """
	print("\x1B[2J\x1B[0;0f", end="")

def getCommand(commandName):
	""" Get a command callback according to the command name """
	try:
		global shellCommands
		command = shellCommands[commandName]
		commandFunction = command[0]
		commandParams = []
		commandFlags  = []
		for item in command[1:]:
			if type(item) == type(""):
				commandParams.append(item)
			if type(item) == type((0,)):
				commandFlags.append(item)
	except  Exception as err:
		# pylint: disable=raise-missing-from
		raise Exception("Command not found '%s'"%commandName)
	return commandName, commandFunction, commandParams, commandFlags

def execCommand(args):
	""" Execute command """
	commandName = ""
	commandFunction = None
	commandParams = []
	commandFlags = []
	try:
		if len(args) >= 1:
			paramsCount = 0
			flags   = {}
			for arg in args:
				arg = arg.strip()
				if len(arg) > 0:
					if commandName == "":
						commandName, commandFunction, commandParams, commandFlags = getCommand(arg)
					else:
						if len(arg) >= 2 and arg[:2] == "--":
							for commandFlag in commandFlags:
								if arg.strip()[2:] == commandFlag[1].strip():
									flags[commandFlag[1]] = commandFlag[2]
									break
							else:
								raise Exception("Illegal option '%s' for"%arg)
						elif arg[0] == "-":
							for commandFlag in commandFlags:
								if arg.strip() == commandFlag[0].strip():
									flags[commandFlag[1]] = commandFlag[2]
									break
							else:
								raise Exception("Illegal option '%s' for"%arg)
						else:
							if paramsCount >= len(commandParams):
								raise Exception("Too many parameters for")
							else:
								flags[commandParams[paramsCount]] = arg
								paramsCount += 1
	except Exception as err:
		# print(useful.exception(err))
		print(err)
		return
	try:
		if commandName.strip() != "":
			commandFunction(**flags)
	except TypeError as err:
		useful.exception(err, msg="Missing parameters for '%s'"%commandName)
	except KeyboardInterrupt:
		print(" [Canceled]")
	except Exception as err:
		useful.exception(err)

def temperature():
	""" Get the internal temperature """
	celcius, farenheit = useful.temperature()
	print("%.2f°C, %d°F"%(celcius, farenheit))

def shell():
	""" Start the shell """
	global shell_exited

	shell_exited = False
	while shell_exited == False:
		try:
			commandLine = ""
			commandLine = input("%s=> "%os.getcwd())
			useful.WatchDog.feed()
		except EOFError:
			print("")
			break
		except KeyboardInterrupt:
			print("Ctr-C detected, use 'exit' to restart server or 'quit' to get python prompt")

		if commandLine.strip() == "quit":
			raise KeyboardInterrupt()
		parseCommandLine(commandLine)

async def asyncShell():
	""" Asynchronous shell """
	import uasyncio
	from server.server import Server

	if useful.ismicropython():
		polling1 = 2
		polling2 = 0.01
	else:
		polling1 = 0.1
		polling2 = 0.5
	while 1:
		# If key pressed
		if useful.kbhit(polling2):
			character = useful.getch()[0]

			# Check if character is correct to start shell
			if not ord(character) in [0,0xA]:
				# Ask to suspend server during shell
				Server.suspend()

				# Wait all server suspended
				await Server.waitAllSuspended()

				# Extend watch dog duration
				useful.WatchDog.start(useful.LONG_WATCH_DOG*2)

				# Get the size of screen
				useful.refreshScreenSize()

				# Start shell
				print("")
				useful.logError("<"*10+" Enter shell " +">"*10)
				shell()
				print("")
				useful.logError("<"*10+" Exit  shell " +">"*10)

				# Restore default path
				uos.chdir("/")

				# Resume watch dog duration
				useful.WatchDog.start(useful.SHORT_WATCH_DOG)

				# Resume server
				Server.resume()
		else:
			await uasyncio.sleep(polling1)


shellCommands = \
{
	"cd"       :[cd       ,"directory"],
	"pwd"      :[pwd      ],
	"cat"      :[cat      ,"file"],
	"cls"      :[cls      ],
	"mkdir"    :[mkdir    ,"directory",            ("-r","recursive",True)],
	"mv"       :[mv       ,"source","destination"],
	"rmdir"    :[rmdir    ,"directory",            ("-r","recursive",True),("-f","force",True),("-q","quiet",True),("-s","simulate",True)],
	"cp"       :[cp       ,"source","destination", ("-r","recursive",True),("-q","quiet",True)],
	"rm"       :[rm       ,"file",                 ("-r","recursive",True),("-f","force",True),("-s","simulate",True)],
	"ls"       :[ls       ,"file",                 ("-r","recursive",True),("-l","long",True)],
	"date"     :[date     ,"offsetUTC" ,           ("-u","update",True),   ("-n","noDst",True)],
	"setdate"  :[setdate  ,"datetime"],
	"uptime"   :[uptime   ],
	"find"     :[find     ,"file"],
	"run"      :[useful.import_  ,"filename"],
	"edit"     :[edit     ,"file"],
	"exit"     :[exit     ],
	"gc"       :[gc       ],
	"grep"     :[grep     ,"text","file",          ("-r","recursive",True),("-i","ignorecase",True),("-e","regexp",True)],
	"mount"    :[mountsd  ,"mountpoint"],
	"umount"   :[umountsd ,"mountpoint"],
	"temperature":[temperature],
	"meminfo"  :[useful.meminfo  ],
	"flashinfo":[useful.flashinfo],
	"sysinfo"  :[useful.sysinfo  ],
	"deepsleep":[deepsleep],
	"ping"     :[ping      ,"host"],
	"reboot"   :[reboot   ],
	"help"     :[help     ],
	"man"      :[man      ,"command"],
	"df"       :[df       ,"mountpoint"],
	"ip2host"  :[ip2host  ,"ipaddress"],
	"host2ip"  :[host2ip  ,"hostname"],
}

if __name__ == "__main__":
	shell()