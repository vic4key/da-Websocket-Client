import sys, trace
from threading import Thread

class StoppableThread(Thread):
	""" A class that represents a stoppable thread of control.
	thread = StoppableThread(target=<function>)
	thread.start()
	# do something
	thread.stop()
	"""

	def __init__(self, *args, **keywords):
		Thread.__init__(self, *args, **keywords)
		self.m_killed = False

	def start(self):
		self.__run_backup = self.run
		self.run = self.__run
		Thread.start(self)

	def stop(self):
		self.m_killed = True

	def __run(self):
		# PYDEV DEBUGGER WARNING: sys.settrace() should not be used when the debugger is being used.
		# sys.settrace(self.globaltrace)
		self.__run_backup()
		self.run = self.__run_backup

	def globaltrace(self, frame, why, arg):
		if why == "call":
			return self.localtrace
		else:
			return None

	def localtrace(self, frame, why, arg):
		if self.m_killed:
			if why == "line":
				raise SystemExit()
		return self.localtrace
