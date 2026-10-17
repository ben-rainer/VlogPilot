'''
main

VlogPilot's primary module, run on the board.

Written in MicroPython for the Raspberry Pi Pico 2 W.
'''

import network
import socket
import time
from machine import Pin

# NETWORK DEFINITIONS
# This network will be broadcast as an access point. Please always keep your device within 1 m of the Pico.
SSID = "VlogPilot AP"
PWD  = "Password123"  # Must be at least 8 characters

# Start the network
ap = network.WLAN(network.AP_IF)
ap.config(essid=SSID, password=PWD)
ap.active(True)

# Wait for the access point to become active
while not ap.active():
    time.sleep(0.2)

# Get the Pi's IP address
ip = ap.ifconfig()[0]
print(f"AP Active: '{SSID}'")
print(f"Access Point IP: {ip}")

# HTML sent to web browsers
def build_html():
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Pico 2 W Control</title>
</head>
<body>
    <p>You are connected!</p>
</body>
</html>"""

# Continuously listen for HTTP connections
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(addr)
server.listen(2)

print(f"HTTP Server listening on http://{ip}:80")

while True:
    try:
        client, client_addr = server.accept()
        raw_request = client.recv(1024).decode("utf-8")
        
        # Parse the HTTP request line (e.g., "GET /led/on HTTP/1.1")
        if raw_request:
            request_line = raw_request.split("\r\n")[0]
        
        # Send HTTP 200 response headers and HTML body
        body = build_html()
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