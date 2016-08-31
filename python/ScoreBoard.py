# finally, directly using sysfs access to GPIO is simple and works

from time import sleep, time
import thread, signal
import math

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
	# duration of buzzing
	buzzDuration = 0.2

	data = dataInitialValues.copy()

	timer = None
	chronoRunning = False

	onModifiedCallback = None

	def __init__(self, onModifiedCallback = None):
		self.onModifiedCallback = onModifiedCallback
		self.update()
		signal.signal(signal.SIGALRM, self.endBuzz)

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
			modified |= self._setValue("Buzzer", Buzzer)
		if modified:
			self.update()
		return modified

	def startChrono(self, minutes, seconds = 0):
		self.stopChrono()
		self.endTime = time() + seconds + 60 * minutes
		self.chronoRunning = True
		self.timer = thread.start_new_thread(self._tick, ())

	def restartChrono(self):
		self.startChrono(self.data["Minutes"], self.data["Seconds"])

	def _tick(self):
		while self.chronoRunning:
			remain = int(math.ceil(self.endTime - time()))
			if remain <= 0:
				self.buzz()
				self.chronoRunning = False

			seconds = remain % 60
			minutes = int(math.floor(remain / 60))

			if self.set(Minutes = minutes, Seconds = seconds) and self.onModifiedCallback:
				self.onModifiedCallback()

			sleep(0.1)
		self.timer = None

	def buzz(self):
		if self.buzzDuration == 0:
			return
		self.set(Buzzer = True)
		signal.setitimer(signal.ITIMER_REAL, self.buzzDuration)

	# sigalarm callback
	def endBuzz(self, signum, frame):
		self.set(Buzzer = False)

	def stopChrono(self):
		if self.timer is not None:
			self.chronoRunning = False

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
