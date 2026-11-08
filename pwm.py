'''
Basic PWM playground

Run this program on the board to move a servo
'''
from machine import Pin, PWM
import time

# Choose the GPIO pin
pin = Pin(14, Pin.OUT)

pwm = PWM(pin, freq=50, duty_u16=32768)  # create a PWM object on a pin
                                         # and set freq 50 Hz and duty 50%


'''
For 180 degree servos, the following applies:
    2300 microseconds = 90 deg
    1500 microseconds = 0 deg
    0500 microseconds = -90 deg

For 360 degree servos, 1500 microseconds means "stop". The distance of the number from this value tells it what speed to run at. 

Must always be an integer.
'''

# Frequency. Generally we leave this at 50.
f = 50

# Initialize the Pulse Width Modulation command
# This would move a 180 servo to somewhere slightly >0 degrees
# This would tell a 360 servo to move slowly in a positive direction
pwm.init(freq=f, duty_u16=32768, duty_ns=1600 * 1000)

time.sleep(1.5)

# Change the command
pwm.init(freq=f, duty_u16=32768, duty_ns=1400 * 1000)

time.sleep(1.5)

# Stop the command
pwm.deinit()