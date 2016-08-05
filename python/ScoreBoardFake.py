# finally, directly using sysfs access to GPIO is simple and works

from time import sleep, time
from os import path
import thread

class ScoreBoard:
	dataInitialValues = {
		"BV" : 0,
		"BL" : 0,
		"FV" : 0,
		"FL" : 0,
		"Minutes": 0,
		"Seconds": 0,
		"Buzzer" : False
	}
	data = dataInitialValues.copy()

	timer = None
	chronoRunning = False

	clockDelay = 50
	dataDelay = 5
	
	onModifiedCallback = None

	def __init__(self, _c, _d, onModifiedCallback = None):
		self.onModifiedCallback = onModifiedCallback
		self.update()

	def reset(self):
		self.stopChrono()
		self.data = self.dataInitialValues.copy()
		self.update()

	def _setValue(self, entry, value):
		if value == '-':
			if self.data[entry] > 0:
				self.data[entry] -= 1
				return True
		elif value == '+':
			return True
			self.data[entry] += 1
		else:
			if entry == 'Buzzer':
				newValue = bool(value)
			else:
				newValue = int(value)
			if self.data[entry] != newValue:
				self.data[entry] = newValue
				return True
		return False

	def set(self, BV=None, BL=None,
		FV=None, FL=None,
		Minutes=None, Seconds=None,
		Buzzer=None):
		modified = False
		if BV is not None:
			modified |= self._setValue("BV", BV)
		if BL is not None:
			modified |= self._setValue("BL", BL)
		if FV is not None:
			modified |= self._setValue("FV", FV)
		if FL is not None:
			modified |= self._setValue("FL", FL)
		if Minutes is not None:
			modified |= self._setValue("Minutes", Minutes)
		if Seconds is not None:
			modified |= self._setValue("Seconds", Seconds)
		if Buzzer is not None:
			modified |= self._setValue("Buzzer", Seconds)
		if modified:
			self.update()
		return modified

	def startChrono(self, minutes, seconds = 0):
		self.stopChrono()
		self.endTime = int(time()) + seconds + 60 * minutes
		self.chronoRunning = True
		self.timer = thread.start_new_thread(self._tick, ())

	def restartChrono(self):
		self.startChrono(self.data["Minutes"], self.data["Seconds"])

	def _tick(self):
		while self.chronoRunning:
			remain = self.endTime - int(time())
			if remain <= 0:
				self.chronoRunning = False
				remain = 0

			seconds = remain % 60
			minutes = int(remain / 60)

			if self.set(Minutes = minutes, Seconds = seconds) and self.onModifiedCallback:
				self.onModifiedCallback()
			if remain == 0:
				self.chronoRunning = False

			sleep(0.1)
		self.timer = None

	def stopChrono(self):
		if self.timer is not None:
			self.chronoRunning = False

	def blank(self):
		print "All Board Off"

	def test(self):
		print "Board AutoTest ..."


	def update(self):
		print "Time {0:02}:{1:02}\nLocal : {2:01} / {3:02}\tVisitors {4:01} / {5:02}".format(
			self.data["Minutes"], self.data["Seconds"],
			self.data["FL"], self.data["BL"],
			self.data["FV"], self.data["BV"])

if __name__ == '__main__':
	sb = ScoreBoard(14, 15)
	sb.test()
	sb.startChrono(0, 10)
	sleep(12)
	sb.blank()

#	with GpioPort(4) as port4:
#		print 'start', time()
##
##		for i in range(0, 10000):
##			port4.high()
##			sleep(0.000001)
##			port4.low()
##			sleep(0.000001)
#		for i in range(0, 2):
#			port4.high()
#			sleep(0.5)
#			port4.low()
#			sleep(0.5)
#
#		print 'end', time()
