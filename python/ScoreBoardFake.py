# finally, directly using sysfs access to GPIO is simple and works

from time import sleep, time
from os import path
import thread
import math
from ScoreBoard import ScoreBoard

class ScoreBoardFake(ScoreBoard):

	def __init__(self, onModifiedCallback = None):
		ScoreBoard.__init__(self, onModifiedCallback)

	def blank(self):
		print "All Board Off"

	def test(self):
		print "Board AutoTest ..."


	def update(self):
		print "Time {0:02}:{1:02}{6}\nLocal : {2:01} / {3:02}\tVisitors {4:01} / {5:02}".format(
			self.data["Minutes"], self.data["Seconds"],
			self.data["FL"], self.data["BL"],
			self.data["FV"], self.data["BV"],
			" buzzing" if self.data["Buzzer"] else "")

if __name__ == '__main__':
	sb = ScoreBoardFake()
	sb.test()
	sb.startChrono(0, 10)
	sleep(12)
	sb.blank()
