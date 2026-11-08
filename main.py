'''
main

VlogPilot's primary module, run on the board.

Written in MicroPython for the Raspberry Pi Pico 2 W.
Uses a MicroDot server running asynchronously so that multiple commands can be run concurrently.
'''

import network
import time
import uasyncio as asyncio
from machine import Pin, PWM

# Import the on-board compiled Microdot library. 
# The error is suppressed in this case.
from microdot import Microdot # type: ignore

time.sleep(2)

# Define the Motor GPIO Pins
m_x = Pin(14, Pin.OUT) # 360deg servo
m_y = Pin(16, Pin.OUT) # 180deg servo

# Motor PWM instances
pwm_x = PWM(m_x, freq=50, duty_u16=32768) # freq 50Hz, duty 50%
pwm_y = PWM(m_y, freq=50, duty_u16=32768)

# Define the indicator LED. We will turn this on when the MicroDot server is successfully defined.
i_led = Pin("LED", Pin.OUT)
i_led.off()

# ----------------------------------------------------
# 1. Setup Wi-Fi Access Point Network (AP Mode)
# ----------------------------------------------------
SSID = "Pico2W-C4"
PASSWORD = "Password123"  # Minimum 8 characters for WPA2

# Create a wireless access point with preset SSID and IP settings, then turn it on
ap = network.WLAN(network.AP_IF)
ap.ifconfig(('192.168.4.1', '255.255.255.0', '192.168.4.1', '192.168.4.1'))
ap.config(essid=SSID, password=PASSWORD)
ap.active(True)

# Wait for the access point to become active
while not ap.active():
    time.sleep(0.2)

# Get the Pi's IP address
ip = ap.ifconfig()[0]
print(f"AP Active: '{SSID}'")
print(f"Access Point IP: {ip}")

# The website will be visitable at http://192.168.4.1/ on connected devices.

# ----------------------------------------------------
# 2. Define the Microdot server
# ----------------------------------------------------

app = Microdot()

# When the user requests the webpage located at "/", return this content
# Note the content header at the end of the return statement so the browser interprets it as a webpage and not text.
@app.route('/')
async def index(request):
    return f"""<!DOCTYPE html><meta content="width=device-width,initial-scale=1"name=viewport><title>VlogPilot Prototype</title><style>button{{border:1px solid #fff;color:#fff;padding:6px;background-color:#000;width:100px;height:100px;font-size:300%}}button:hover{{background-color:#0f0f0f}}.interface,body,html{{background-color:#000;width:100%;height:100%;padding:0;margin:0}}.interface{{display:flex;justify-content:center;align-items:center;flex-direction:column}}.row{{display:flex}}</style><script>function f(f){{fetch(`./motor/${{f}}/`)}}</script><body><d class=interface><d class=row><button onclick='f("stopx")'>x</button> <button onclick='f("up")'>&#9650;</button> <button></button></d><d class=row><button onclick='f("left")'>&#9664;</button> <button onclick='f("reset")'>o</button> <button onclick='f("right")'>&#9654;</button></d><d class=row><button></button> <button onclick='f("down")'>&#9660;</button> <button></button></d></d>""", {'Content-Type': 'text/html'}

# Action to do when the motor is moved. We must return some content to the client, so we sent the string 'sent' to indicate that the request was processed
# Defined asynchronously so that other things may happen concurrently.
@app.route('/motor/up/')
async def motorup(request):
    # Send a PWM to the motor
    pwm_y.init(freq=50, duty_u16=32768, duty_ns=2300 * 1000) # 90 deg

    return 'sent'

@app.route('/motor/down/')
async def motordown(request):
    # Send a PWM to the motor
    pwm_y.init(freq=50, duty_u16=32768, duty_ns=500 * 1000) # -90 deg

    return 'sent'

@app.route('/motor/left/')
async def motorleft(request):
    # Send a PWM to the motor
    pwm_x.init(freq=50, duty_u16=32768, duty_ns=1525 * 1000) # 90 deg

    return 'sent'

@app.route('/motor/right/')
async def motorright(request):
    # Send a PWM to the motor
    pwm_x.init(freq=50, duty_u16=32768, duty_ns=1425 * 1000) # -90 deg

    return 'sent'

@app.route('/motor/stopx/')
async def motorstopx(request):
    # Send a PWM to the motor
    pwm_x.init(freq=50, duty_u16=32768, duty_ns=1500 * 1000) # stop

    return 'sent'

@app.route('/motor/reset/')
async def reset(request):
    # Send a PWM to the motor
    pwm_x.init(freq=50, duty_u16=32768, duty_ns=1500 * 1000) # stop
    pwm_y.init(freq=50, duty_u16=32768, duty_ns=1500 * 1000) # 0 deg

    return 'sent'

# Since all routes were defined successfully, light the onboard indicator LED
i_led.on()

# Asynchronously run the MicroDot app. This should be the last command in the file.
asyncio.run(app.start_server(host='0.0.0.0', port=80))