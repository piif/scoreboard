# finally, directly using sysfs access to GPIO is simple and works

from time import sleep, time
from os import path
import thread

class ScoreBoard:
	BV = 0
	BL = 0
	FV = 0
	FL = 0
	Minutes = 0
	Seconds = 0
	Buzzer = False

	timer = None
	chronoRunning = False

	clockDelay = 50
	dataDelay = 5

	def __init__(self, _c, _d):
		self.update()

	def _setValue(self, before, value):
		if value == '-':
			return before - 1
		elif value == '+':
			return before + 1
		else:
			return int(value)

	def set(self, BV=None, BL=None,
		FV=None, FL=None,
		Minutes=None, Seconds=None,
		Buzzer=None):
		if BV is not None:
			self.BV = self._setValue(self.BV, BV)
		if BL is not None:
			self.BL = self._setValue(self.BL, BL)
		if FV is not None:
			self.FV = self._setValue(self.FV, FV)
		if FL is not None:
			self.FL = self._setValue(self.FL, FL)
		if Minutes is not None:
			self.Minutes = self._setValue(self.Minutes, Minutes)
		if Seconds is not None:
			self.Seconds = self._setValue(self.Seconds, Seconds)
		if Buzzer is not None:
			self.Buzzer = bool(Buzzer)
		self.update()

	def startChrono(self, minutes, seconds = 0):
		self.stopChrono()
		self.endTime = int(time()) + seconds + 60 * minutes
		self.chronoRunning = True
		self.timer = thread.start_new_thread(self._tick, ())

	def restartChrono(self):
		self.startChrono(self.Minutes, self.Seconds)

	def _tick(self):
		while self.chronoRunning:
			remain = self.endTime - int(time())
			if remain <= 0:
				self.chronoRunning = False
				remain = 0

			seconds = remain % 60
			minutes = int(remain / 60)

			self.set(Minutes = minutes, Seconds = seconds)
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
			self.Minutes, self.Seconds,
			self.FL, self.BL,
			self.FV, self.BV)

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
