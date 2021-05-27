
import machine, onewire, ds18x20, time

led = machine.Pin(25, machine.Pin.OUT)
ds_pin = machine.Pin(4)
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
    self.start_time = time.time_ns()
    self.delta_t = 0
  def update(self):
    # calculate time since start time and update timer time
    self.delta_t = time.time_ns() - self.start_time
  def reset(self):
    # reset timer
    self.start_time = 0
    self.delta_t = 0

test_temp = 40

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
    time.sleep_ms(750)
    self.temp = ds_sensor.read_temp(roms[self.sensor_index]) + test_temp
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
kettle.set_target_temp(67)

timer = Timer()
timer.start()

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

  timer.update()
  kettle.read_temp_sensor()
  kettle.update_heating()
  if kettle.heating_state == 1:
    relay.value(0)
  else:
    relay.value(1)
  print("Current kettle temperature: " + str(kettle.temp) + "°C")
  #print("Heating: " + str(kettle.heating_state))
  # coole Lightshow
  led.value(1)
  time.sleep_ms(250)
  led.value(0)
  time.sleep_ms(250)
  led.value(1)
  time.sleep_ms(250)
  led.value(0)
  time.sleep(1)
  

