# finally, directly using sysfs access to GPIO is simple and works

from time import sleep, time
from os import path

from ScoreBoard import ScoreBoard

class ScoreBoardImpl(ScoreBoard):
	devicePath = "/dev/scoreboard"

	def __init__(self, onModifiedCallback = None):
		if not path.exists(self.devicePath):
			raise Exception("must load module and create device")
		self.device = open(self.devicePath, 'w', 0)
		ScoreBoard.__init__(self, onModifiedCallback)

	def blank(self):
		toSend = ' ' * 11
		self.send(toSend)

	def test(self):
		toSend = '0123456789Z'
		self.send(toSend)
		sleep(0.1)
		toSend = '9876543210 '
		self.send(toSend)
		sleep(2)
		self.update()

	def update(self):
		toSend = ''
		# BVu;
		toSend += str( self.data["BV"] % 10 )
		# BVd;
		toSend += str( int(self.data["BV"] / 10) )
		# FV;
		toSend += str( self.data["FV"] )
		# BLu;
		toSend += str( self.data["BL"] % 10 )
		# BLd;
		toSend += str( int(self.data["BL"] / 10) )
		# FL;
		toSend += str( self.data["FL"] )
		# Md;
		toSend += str( int(self.data["Minutes"] / 10) )
		# Mu;
		toSend += str( self.data["Minutes"] % 10 )
		# Sd;
		toSend += str( int(self.data["Seconds"] / 10) )
		# Su;
		toSend += str( self.data["Seconds"] % 10 )
		# Bz;
		if self.data["Buzzer"]:
			toSend += 'Z'
		else:
			toSend += ' '
		self.send(toSend)

	def send(self,str):
		self.device.write(str)


if __name__ == '__main__':
	sb = ScoreBoardImpl()
	sb.test()
	sb.startChrono(0, 10)
	sleep(12)
	sb.blank()
