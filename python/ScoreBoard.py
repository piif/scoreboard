# finally, directly using sysfs access to GPIO is simple and works

from time import sleep, time
from os import path
import thread

rootdir= "/sys/class/gpio"


class GpioPort:
	port = None
	filename = None
	file = None

	def __init__(self, port):
		self.port = str(port)
		self.filename = "{}/gpio{}/value".format(rootdir, port)
		isVisible = path.exists(self.filename)
		if not isVisible:
			f = open('{}/export'.format(rootdir), 'w', 0)
			f.write(self.port)
			f.close()
			sleep(0.1)
		f = open('{}/gpio{}/direction'.format(rootdir, self.port), 'w', 0)
		f.write("out")
		f.close()
		sleep(0.1)
		self.file = open(self.filename, 'w', 0)
		print self.filename, self.file
	
	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
                self.file.close()
		isVisible = path.exists(self.filename)
		if isVisible:
			f = open('{}/unexport'.format(rootdir), 'w', 0)
			f.write(self.port)
			f.close()
			sleep(0.1)

	def low(self):
		self.file.write("0")
	def high(self):
		self.file.write("1")

def pause(n):
	#before=time()
	for i in range(0,n):
		pass
	#after=time()
	#print ((after - before) * 1000), "ms"

class ScoreBoard:
	data = None
	clock = None

	digits = (
	 '0000111111', # 0
	 '0000000110', # 1
	 '0001011011', # 2
	 '0001001111', # 3
	 '0001100110', # 4
	 '0001101101', # 5
	 '0001111101', # 6
	 '0000000111', # 7
	 '0001111111', # 8
	 '0001101111', # 9
	)
	buzzerOn  = '1000000000'
	buzzerOff = '0000000000'

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

	def __init__(self, clock, data):
		self.clock = GpioPort(clock)
		self.clock.high()
		self.data = GpioPort(data)
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
		toSend = '0' * 110
		self.send(toSend)

	def test(self):
		toSend = ''.join(self.digits) + self.buzzerOn
		self.send(toSend)
		sleep(0.1)
		toSend = ''.join(self.digits) + self.buzzerOff
		self.send(toSend)
		sleep(2)
		toSend = '1' * 100 + '0' * 10
		self.send(toSend)
		sleep(2)
		self.update()

	def update(self):
		toSend = ''
		# BVu;
		toSend += self.digits[self.BV % 10]
		# BVd;
		toSend += self.digits[int(self.BV / 10)]
		# FV;
		toSend += self.digits[self.FV]
		# BLu;
		toSend += self.digits[self.BL % 10]
		# BLd;
		toSend += self.digits[int(self.BL / 10)]
		# FL;
		toSend += self.digits[self.FL]
		# Md;
		toSend += self.digits[int(self.Minutes / 10)]
		# Mu;
		toSend += self.digits[self.Minutes % 10]
		# Sd;
		toSend += self.digits[int(self.Seconds / 10)]
		# Su;
		toSend += self.digits[self.Seconds % 10]
		# Bz;
		if self.Buzzer:
			toSend += self.buzzerOn
		else:
			toSend += self.buzzerOff
		self.send(toSend)

	def send(self,str):
		#print "Sending", len(str), "bits"
		before = time()
		for c in str:
			self.data.file.write(c)
			pause(self.dataDelay)
			self.clock.low()
			pause(self.clockDelay)
			self.clock.high()
			pause(self.clockDelay)
		after = time()
		#print "Took", ((after - before) * 1000), "ms"

if __name__ == '__main__':
	sb = ScoreBoard(14,15)
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
