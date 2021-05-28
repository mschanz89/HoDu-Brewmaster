


import machine, onewire, ds18x20, time
from machine import Pin, I2C
import sh1106
from time import sleep

i2c = I2C(scl=Pin(22), sda=Pin(21))

oled_width = 128
oled_height = 64
oled = sh1106.SH1106_I2C(oled_width, oled_height, i2c, None, 0x3c)
oled.rotate(True)

led = machine.Pin(25, machine.Pin.OUT)

ds_pin = machine.Pin(12)
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()
print('Found DS devices: ', roms)
relay = machine.Pin(26, Pin.OUT)


class Timer:
  def __init__(self):
    self.start_time = 0
    self.delta_t = 0
  def start(self):
    # set system time as start time
    self.start_time = time.time()
    self.delta_t = 0
  def update(self):
    # calculate time since start time and update timer time
    self.delta_t = time.time() - self.start_time
  def reset(self):
    # reset timer
    self.start_time = 0
    self.delta_t = 0
    

class Kettle:
  def __init__(self, sensor_index):
    self.sensor_index = sensor_index
    self.temp = 0
    self.target_temp = 0
    self.heat = 0 # 0: off, 1: keep temp, 2: ramp up temp to target_temp
    self.heating_state = 0 # 0:heating off, 1: heating on
    self.hysteresis = 2
  def set_target_temp(self, target_temp):
    self.target_temp = target_temp
    if target_temp > self.temp:
      self.heat = 2
  def set_heating_state(self, heating_state):
    self.heating_state = heating_state
  def set_heat(self, heat):
    self.heat = heat
  def read_temp_sensor(self):
    ds_sensor.convert_temp()
    time.sleep_ms(1000)
    self.temp = ds_sensor.read_temp(roms[self.sensor_index])
  def update_heating(self):
    if self.temp < self.target_temp:
      if self.heat == 1 and self.temp > self.target_temp-self.hysteresis:
        #switch off heating
        self.heating_state = 0
      else:
        #switch on heating
        self.heat = 2
        self.heating_state = 1
    else:
      #switch off heating
      self.heat = 1
      self.heating_state = 0
    

kettle = Kettle(0) 

timer = Timer()
timer.start()


# Initialisiere Rasten
temp_list = [55, 62, 67, 72, 78]
duration_list = [15, 15, 30, 30, 15]
if len(temp_list) != len(duration_list):
  oled.fill(0)
  oled.text("Error:", 0, 0)
  oled.text("Unequal list of", 0, 10)
  oled.text("temperatures and", 0, 20)
  oled.text("durations", 0, 30)
  oled.show()
  time.sleep(600)
level_index = 0
kettle.set_target_temp(temp_list[level_index])

while True:

  #conn, addr = s.accept()
  #print('Got a connection from %s' % str(addr))
  #request = conn.recv(1024)
  #request = str(request)

  #port_on = request.find('/?schlampe=on')
  #port_off = request.find('/?schlampe=off')

  #if port_on == 6:
  #  schlampe.value(1)
  #if port_off == 6:
  #  schlampe.value(0)

  #print('Content = %s' % str(request))
  #response = web_page()
  #conn.send('HTTP/1.1 200 OK\n')
  #conn.send('Content-Type: text/html\n')
  #conn.send('Connection: close\n\n')
  #conn.sendall(response)
  #conn.close()
  
  #oled.sleep(False)
  oled.fill(0)
  timer.update()
  kettle.read_temp_sensor()
  oled.text("Temp: " + str(kettle.temp), 0, 0)
  oled.text("Set temp: " + str(temp_list[level_index]), 0, 10)
  kettle.update_heating()
  if kettle.heating_state == 1:
    relay.value(0)
    oled.text("Heating: ON", 0, 20)
  else:
    relay.value(1)
    oled.text("Heating: OFF", 0, 20)

  oled.text("Time: " + str(timer.delta_t), 0, 30)

  oled.show()
  



