# first try to tests GPIO basics

import gpiozero, signal
from time import sleep

# prepare led
led=gpiozero.LED(4)

# function to make it blink
def blink_sighandler(signum, frame):
	global ttl
	if ttl > 0:
		led.toggle()
		ttl -= 1

# call handler every 500ms
signal.signal(signal.SIGALRM, blink_sighandler)
signal.setitimer(signal.ITIMER_REAL, 0.1, 0.001)

ttl = 10000
while ttl:
	signal.pause()

# and cancel timer
signal.setitimer(signal.ITIMER_REAL, 0)

print '.'
