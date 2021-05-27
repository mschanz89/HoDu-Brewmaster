try:
  import usocket as socket
except:
  import socket

import network
from machine import Pin

import esp
esp.osdebug(None)

import gc
gc.collect()

ssid = 'Brauschlampe'
password = '123456789'

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password)

while ap.active() == False:
  pass

print('Connection successful')
print(ap.ifconfig())

schlampe = Pin(18, Pin.OUT)
schlampe.value(0)

def web_page():
  html = """<html><head> <title>Brauschlampe Hardt!</title> <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
  h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #13b002; border: none; 
  border-radius: 4px; color: white; padding: 14px 20px; text-decoration: none; font-size: 15px; margin: 2px; cursor: pointer;}
  .button2{background-color: #b50000;}.button3{background-color: #a8a8a8;}</style></head>
  <body>
  <h1>Brauschlampe 1.0</h1>
  <p><a href="/?schlampe=on"><button class="button">PNEIS ON</button></a></p>
  <p><a href="/?schlampe=off"><button class="button button2">STOP</button></a></p>
  </body></html>"""
  return html

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
  conn, addr = s.accept()
  print('Got a connection from %s' % str(addr))
  request = conn.recv(1024)
  request = str(request)

  port_on = request.find('/?schlampe=on')
  port_off = request.find('/?schlampe=off')

  if port_on == 6:
    schlampe.value(1)
  if port_off == 6:
    schlampe.value(0)

  print('Content = %s' % str(request))
  response = web_page()
  conn.send('HTTP/1.1 200 OK\n')
  conn.send('Content-Type: text/html\n')
  conn.send('Connection: close\n\n')
  conn.sendall(response)
  conn.close()