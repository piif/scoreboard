# tests RPIO lib instead of gpiozero

from RPIO import PWM
from time import sleep

# Setup PWM and DMA channel 0
PWM.setup()
PWM.init_channel(0)

# Add some pulses to the subcycle
PWM.add_channel_pulse(0, 4, 0, 50)
PWM.add_channel_pulse(0, 4, 100, 50)

sleep(10)

# Stop PWM for specific GPIO on channel 0
PWM.clear_channel_gpio(0, 4)

# Shutdown all PWM and DMA activity
PWM.cleanup()
