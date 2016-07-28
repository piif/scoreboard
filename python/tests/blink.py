# tests RPi.GPIO lib instead of gpiozero

from time import sleep
import RPi.GPIO as GPIO
import signal

# numeroter par "ports"
GPIO.setmode(GPIO.BCM)

# prepare led
GPIO.setup(4, GPIO.OUT, initial=GPIO.LOW)

pwm = GPIO.PWM(4, 10000)
print 'start'
pwm.start(25)

sleep(10)

print 'stop'
pwm.stop()

GPIO.cleanup()
print '.'
