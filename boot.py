try:
  import usocket as socket
except:
  import socket

from machine import Pin, SoftI2C
import network, onewire_a, ds18x20_a, time, sh1106

import esp
esp.osdebug(None)

import gc
gc.collect()

# init display
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = sh1106.SH1106_I2C(128, 64, i2c, None, 0x3c)
oled.rotate(True)
oled.text('Booting ...', 0, 0)
oled.show()

# init network
ssid = 'Brauschlampe'
password = '123456789'

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=ssid, password=password)

while ap.active() == False:
  pass

print(ap.ifconfig())
oled.text('Network OK', 0, 10)
oled.text(ap.ifconfig()[0], 0, 20)
oled.show()

# init stupid LED
led = Pin(25, Pin.OUT)

# init relais
rel1 = Pin(26, Pin.OUT)
rel2 = Pin(27, Pin.OUT)

# init sensors
ds_init = Pin(19, Pin.OUT)
ds_init.value(1)
ds_sensor = ds18x20_a.DS18X20(onewire_a.OneWire(Pin(19)))
time.sleep_ms(2000)
oled.text('DS Scan', 0, 30)
oled.show()

roms = ds_sensor.scan()
time.sleep_ms(2000)
print('Found DS devices: ', roms)
oled.text('{} sensors found'.format(len(roms)), 0, 40)
oled.show()