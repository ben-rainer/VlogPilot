'''
main

VlogPilot's primary module, run on the board.

Written in MicroPython for the Raspberry Pi Pico 2 W.
'''
import network
import socket
import time
from machine import Pin

# On the Pico 2 W / Pico W, the onboard LED is driven via the CYW43 Wi-Fi chip:
led = Pin("LED", Pin.OUT)
led.off()

# ----------------------------------------------------
# 1. Setup Access Point (AP Mode)
# ----------------------------------------------------
SSID = "Pico2W-Control"
PASSWORD = "Password123"  # Minimum 8 characters for WPA2

ap = network.WLAN(network.AP_IF)
ap.config(essid=SSID, password=PASSWORD)
ap.active(True)

while not ap.active():
    time.sleep(0.2)

ip = ap.ifconfig()[0]
print(f"AP Active: '{SSID}'")
print(f"Access Point IP: {ip}")

# ----------------------------------------------------
# 2. HTML Template
# ----------------------------------------------------
def build_html(state):
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Pico 2 W Control</title>
    <style>
        body {{ font-family: sans-serif; text-align: center; margin-top: 40px; background: #f4f4f9; }}
        h1 {{ color: #333; }}
        .btn {{ display: inline-block; padding: 14px 28px; font-size: 18px; text-decoration: none; border-radius: 8px; color: white; margin: 10px; }}
        .on {{ background-color: #28a745; }}
        .off {{ background-color: #dc3545; }}
        .status {{ font-size: 20px; font-weight: bold; margin-bottom: 20px; }}
    </style>
</head>
<body>
    <h1>Pico 2 W Web Controller</h1>
    <p class="status">LED Status: <span>{state}</span></p>
    <p>
        <button type="button" class="btn on" onclick="measureLatency(event, 'on')">Turn ON</button>
        <button type="button" class="btn off"  onclick="measureLatency(event, 'off')">Turn OFF</button>
    </p>
    
    <p id= "latency">Response time: -- ms</p>
    <script>
    async function measureLatency(event, command) {{

        const start = performance.now();

        try {{
            const response = await fetch('/led/' + command);

            if (!response.ok) {{
                throw new Error('Command failed');
            }}
            await response.text();

            const latency = performance.now()- start;

            document.getElementById('latency').textContent =
                'Response time: ' + latency.toFixed(2) + ' ms';

            document.querySelector('.status span').textContent =
                command.toUpperCase();

        }} catch (error) {{
            document.getElementById('latency').textContent =
                'Measurement failed';
        }}
    }}
    </script>


</body>
</html>"""

# ----------------------------------------------------
# 3. HTTP Server Loop
# ----------------------------------------------------
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(addr)
server.listen(2)

print(f"HTTP Server listening on http://{ip}:80")

led_state = "OFF"

while True:
    try:
        client, client_addr = server.accept()
        raw_request = client.recv(1024).decode("utf-8")
        
        # Parse the HTTP request line (e.g., "GET /led/on HTTP/1.1")
        if raw_request:
            request_line = raw_request.split("\r\n")[0]
            
            if "GET /led/on" in request_line:
                led.on()
                led_state = "ON"
            elif "GET /led/off" in request_line:
                led.off()
                led_state = "OFF"
        
        # Send HTTP 200 response headers and HTML body
        body = build_html(led_state)
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n\r\n"
            + body
        )
        client.sendall(response)
        client.close()

    except Exception as e:
        print(f"Connection error: {e}")
        try:
            client.close()
        except:
            pass