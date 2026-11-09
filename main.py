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
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>VlogPilot Controller</title>
<style>*{box-sizing:border-box}
body{margin:0;background:#101b16;color:#fff;font-family:Arial,sans-serif}
main{width: 100%;max-width:750px;min-height: 100dvh;margin:auto;padding:12px;display: flex;flex-direction: column;justify-content: center;text-align:center;}
h1{color:#c4d68d;margin-bottom:5px}
p{color:#cbd5c5}
.grid{display:grid;grid-template-columns:repeat(3, minmax(0, 1fr));gap:10px;margin-top:15px}
button{width: 100%;height: clamp(100px, 19dvh, 170px);border:2px solid #a8bf69;border-radius:12px;background:#304b3b;color:white;font-size:30px;cursor:pointer;touch-action:manipulation;}
button:active{background:#719044}
button:focus-visible{outline:3px solid #fff;outline-offset:2px;}
.stop{background:#9d3939;border-color:#d87b7b;font-size:25px;font-weight:bold;}
.reset{font-size:25px;font-weight:bold;color:#18301c;background:#b3c95e;border-color:#578f61;}
.empty{visibility:hidden}
#status{margin-top:20px;color:#c4d68d;font-size:15px}
</style></head><body><main><h1>VlogPilot</h1>
<div class="grid"><button class="stop" onclick="send('stopx')" aria-label="Stop horizontal rotation">STOP</button>
<button onclick="send('up')" aria-label="Tilt up">&#9650;</button><span></span>
<button onclick="send('left')" aria-label="Rotate left">&#9664;</button>
<button class="reset" onclick="send('reset')" aria-label="Reset position">RESET</button>
<button onclick="send('right')" aria-label="Rotate right">&#9654;</button>
<span></span><button onclick="send('down')" aria-label="Tilt down">&#9660;</button>
<span></span></div></main>
<script>function send(cmd) {fetch('/motor/' + cmd + '/').catch(() => {});}</script>    
</body>
</html>""", {'Content-Type': 'text/html'}

    
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
    pwm_x.init(freq=50, duty_u16=32768, duty_ns=1575 * 1000) # 90 deg

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