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
      else:
        #switch on heating
        self.heat = 2
        self.heating_state = 1
    else:
      #switch off heating
      self.heat = 1
      self.heating_state = 0

def zfill(s, width):
  return '{:0>{w}}'.format(s, w=width)

def read_men():
  ad = men.read()
  if ad > 2300 and ad < 2500:
    return 1
  elif ad > 3700 and ad < 3900:
    return 2
  elif ad > 4050:
    return 3
  elif ad > 3100 and ad < 3450:
    return 4

if __name__ == '__main__':
  # init
  kettle = Kettle(0) 
  timer = Timer()
  l_men, l_ttime, l_ttemp, l_brew = False, False, False, False
  start_rast, alarm = False, False

  while True:
    while l_men == False:
      ttime, ttemp = 30, 60
      l_ttime, l_ttemp, l_brew = False, False, False
      oled.fill(0)
      oled.text('BRAUSCHLAMPE 1.0', 0, 0)
      kettle.read_temp_sensor()
      oled.text('Kessel: {0:5.2f}C'.format(kettle.temp), 0, 20)
      oled.text('Soll: N/A', 0, 30)
      oled.text('Heizung: AUS', 0, 40)
      oled.show()
      if read_men() == 3:
        l_men = True
        time.sleep_ms(500)
  
    while l_ttime == False:
      oled.fill(0)
      oled.text('BRAUSCHLAMPE 1.0', 0, 0)
      oled.text('Set time:', 0, 20)
      oled.text('minutes', 20, 30)
      if read_men() == 1:
        ttime += 1
      elif read_men() == 2:
        if ttime > 0:
          ttime -= 1
      elif read_men() == 3:
        l_ttime = True
        l_men, l_ttemp, l_brew = False, False, False
        time.sleep_ms(500)
      elif read_men() == 4:
        l_ttime = True
        time.sleep_ms(500)
      oled.text(str(ttime),0, 30)
      oled.show()
  
    while l_ttemp == False:
      oled.fill(0)
      oled.text('BRAUSCHLAMPE 1.0', 0, 0)
      oled.text('Set time:', 0, 20)
      oled.text(str(ttime), 0, 30)
      oled.text('minutes', 20, 30)
      oled.text('Set temp:', 0, 40)
      oled.text('Celsius', 30, 50)
  
      if read_men() == 1:
        if ttemp < 105:
          ttemp += 1
      elif read_men() == 2:
        if ttemp > 30:
          ttemp -= 1
      elif read_men() == 3:
        l_ttemp = True
        l_men = False
        time.sleep_ms(500)
      elif read_men() == 4:
        l_ttemp = True
        time.sleep_ms(500)
        l_men = False
        kettle.set_target_temp(ttemp)
        ttime = ttime*60
      oled.text(str(ttemp),0, 50)
      oled.show()

    while l_brew == False:
      oled.fill(0)
      oled.text('BRAUSCHLAMPE 1.0', 0, 0)
      #kettle.read_temp_sensor()
      kettle.update_heating()
      oled.text('Kessel: {0:5.2f}C'.format(kettle.temp), 0, 20)
      oled.text('Soll: {0:5.2f}'.format(ttemp), 0, 30)
      if kettle.heating_state == 1:
        rel1.value(1)
        oled.text('Heizung: AN', 0, 40)
      else:
        rel1.value(0)
        oled.text('Heizung: AUS', 0, 40)
        if start_rast == False:
          timer.start()
          start_rast = True
      tms = divmod(ttime-timer.delta_t,60)
      oled.text('Time: {0}:{1}'.format(zfill(str(tms[0]),2),zfill(str(tms[1]),2)), 0, 50)
      oled.show()
      if read_men() == 3:
        l_brew,l_men = True,False
        time.sleep_ms(500)

      if ttime-timer.delta_t < 0:
        l_brew, alarm = True, True
        while alarm == True:
          buzz.value(1)
          time.sleep_ms(1)
          buzz.value(0)
          time.sleep_ms(1)
          if read_men() == 3:
            alarm == False
      if start_rast == True:
        timer.update()