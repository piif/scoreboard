# finally, directly using sysfs access to GPIO is simple and works

from time import sleep, time
from os import path

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

from ScoreBoard import ScoreBoard

class ScoreBoardImpl(ScoreBoard):
	clockPort = None
	dataPort = None

	clockDelay = 50
	dataDelay = 5

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

	def __init__(self, clock, data, onModifiedCallback = None):
		self.clockPort = GpioPort(clock)
		self.clockPort.high()
		self.dataPort = GpioPort(data)
		ScoreBoard.__init__(self, onModifiedCallback)

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
		toSend += self.digits[self.data["BV"] % 10]
		# BVd;
		toSend += self.digits[int(self.data["BV"] / 10)]
		# FV;
		toSend += self.digits[self.data["FV"]]
		# BLu;
		toSend += self.digits[self.data["BL"] % 10]
		# BLd;
		toSend += self.digits[int(self.data["BL"] / 10)]
		# FL;
		toSend += self.digits[self.data["FL"]]
		# Md;
		toSend += self.digits[int(self.data["Minutes"] / 10)]
		# Mu;
		toSend += self.digits[self.data["Minutes"] % 10]
		# Sd;
		toSend += self.digits[int(self.data["Seconds"] / 10)]
		# Su;
		toSend += self.digits[self.data["Seconds"] % 10]
		# Bz;
		if self.data["Buzzer"]:
			toSend += self.buzzerOn
		else:
			toSend += self.buzzerOff
		self.send(toSend)

	def send(self,str):
		#print "Sending", len(str), "bits"
		before = time()
		for c in str:
			self.dataPort.file.write(c)
			pause(self.dataDelay)
			self.clockPort.low()
			pause(self.clockDelay)
			self.clockPort.high()
			pause(self.clockDelay)
		after = time()
		#print "Took", ((after - before) * 1000), "ms"


if __name__ == '__main__':
	sb = ScoreBoardImpl(14, 15)
	sb.test()
	sb.startChrono(0, 10)
	sleep(12)
	sb.blank()
