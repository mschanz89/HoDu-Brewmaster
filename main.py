
# timer class
class Timer:
  def __init__(self):
    self.start_time = 0
    self.delta_t = 0
  def start(self):
    # set system time as start time
    self.start_time = time.time()
  def update(self):
    # calculate time since start time and update timer time
    self.delta_t = time.time() - self.start_time
  def reset(self):
    # reset timer
    self.start_time = 0
    self.delta_t = 0
    
# kettle class
class Kettle:
  def __init__(self, sensor_index):
    self.sensor_index = sensor_index
    self.temp, self.ttemp = 0, 30
    self.target_temp = 0
    self.heat = 0 # 0: off, 1: keep temp, 2: heat up to target_temp
    self.heating_state = 0 # 0:heating off, 1: heating 1/2 on, 2: heating 2/2 on
    self.hysteresis = 2

  def set_target_temp(self, target_temp):
    self.target_temp = target_temp
    if target_temp > self.temp:
      self.heat = 2

  def read_temp_sensor(self):
    ds_sensor.convert_temp()
    time.sleep_ms(100)
    self.ttemp = ds_sensor.read_temp(roms[self.sensor_index])
    if self.temp == 0:
      self.temp = self.ttemp
    if abs(self.ttemp - self.temp) < 2:
      self.temp = self.ttemp

  def update_heating(self):
    self.read_temp_sensor()
    if self.temp < self.target_temp:
      if self.heat == 1 and self.temp > self.target_temp-self.hysteresis:
        #switch off heating
        self.heating_state = 0
      elif self.heat == 2 and self.temp > self.target_temp-self.hysteresis:
        #reduce heating to half power to prevent overheating
        self.heating_state = 1
      else:
        #switch on heating
        self.heat = 2
        self.heating_state = 2
    else:
      #switch off heating
      self.heat = 1
      self.heating_state = 0

def zfill(s, width):
  return '{:0>{w}}'.format(s, w=width)

def read_men():
  ad = men.read()
  # Plus
  #if ad > 2300 and ad < 2500:
  if ad > 1580 and ad < 1680:
    return 1
  # Minus
  #elif ad > 3700 and ad < 3900:
  elif ad > 1400 and ad < 1520:
    return 2
  # Menu

  #elif ad > 4050:
  elif ad > 1790 and ad < 1880:
    return 3
  # Select
  #elif ad > 3100 and ad < 3450:
  elif ad > 1690 and ad < 1780:
    return 4

if __name__ == '__main__':
  # init
  kettle = Kettle(0) 
  timer = Timer()
  l_men, l_ttime, l_ttemp, l_brew = False, False, False, False
  start_rast, alarm = False, False

  while True:
    oled.fill(0)
    oled.text(str(men.read()), 0, 0)
    time.sleep_ms(500)
    oled.show()
