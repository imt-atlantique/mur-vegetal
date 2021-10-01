from m5stack import *
from m5ui import *
from uiflow import *
import wifiCfg
import time
import urequests
import json

import unit

setScreenColor(0x000000)
env1 = unit.get(unit.ENV, unit.PORTA)
earth1 = unit.get(unit.EARTH, unit.PORTB)
relay1 = unit.get(unit.RELAY, unit.PORTC)
earth2 = unit.get(unit.EARTH, (36,35))
relay13 = unit.get(unit.RELAY, (1,2))


screen_is_on = None
margin_top = None
i = None
watering_frequency = None
watering_duration = None

wifiCfg.autoConnect(lcdShow=True)
wifiCfg.reconnect()
wifiCfg.reconnect()
tank = M5Rect(1, 196, 8, 1, 0x729fcf, 0x729fcf)
icon = M5Img(36, 0, "res/icon.png", True)
qr = M5Img(153, 140, "res/qr.jpg", True)
temperature = M5Circle(5, 126, 5, 0x73d216, 0x000000)
humidity = M5Circle(5, 143, 5, 0x73d216, 0x000000)
button0 = M5Img(60, 204, "res/button0.png", True)
tank_border = M5Rect(0, 178, 10, 20, 0x000000, 0xffffff)
level2 = M5Circle(169, 77, 5, 0xef2929, 0x000000)
icons = M5Img(0, 48, "res/icons.png", True)
level1 = M5Circle(169, 93, 5, 0xfcaf3e, 0x000000)
battery_border = M5Rect(164, 130, 16, 10, 0x000000, 0xFFFFFF)
battery = M5Rect(165, 131, 14, 8, 0x73d216, 0x73d216)
button1 = M5Img(136, 204, "res/button1.png", True)

import math
from numbers import Number


# Describe this function...
def draw_ui():
  global screen_is_on, margin_top, i, watering_frequency, watering_duration
  lcd.font(lcd.FONT_DejaVu18)
  lcd.print('Mur vegetal v0.9', 78, 11, 0xffffff)
  temperature.show()
  humidity.show()
  level2.show()
  level1.show()
  speaker.setVolume(0)
  tank_border.show()
  tank.show()
  battery_border.show()
  battery.show()
  icon.show()
  icons.show()
  qr.show()
  button0.show()
  button1.show()
  margin_top = 98
  screen_is_on = True
  i = 0
  watering_frequency = 3600
  watering_duration = 60
  lcd.line(160, 44, 160, 220, 0xffffff)
  lcd.font(lcd.FONT_DejaVu18)
  lcd.print('Air interieur', 0, margin_top, 0xffffff)
  lcd.print('Humidite bacs', 164, 48, 0xffffff)
  lcd.print("Reservoir d'eau", 0, (margin_top + 58), 0xffffff)
  lcd.print('Batterie', 164, 106, 0xffffff)


def buttonA_wasPressed():
  global screen_is_on, margin_top, i, watering_frequency, watering_duration
  if screen_is_on:
    lcd.setBrightness(0)
    screen_is_on = False
  else:
    lcd.setBrightness(30)
    screen_is_on = True
  pass
btnA.wasPressed(buttonA_wasPressed)

def buttonB_pressFor():
  global screen_is_on, margin_top, i, watering_frequency, watering_duration
  relay1.on()
  wait(60)
  relay1.off()
  wait(10)
  relay13.on()
  wait(60)
  relay13.off()
  pass
btnB.pressFor(0.8, buttonB_pressFor)


lcd.setBrightness(30)
setScreenColor(0x000000)
while True:
  draw_ui()
  lcd.font(lcd.FONT_Ubuntu)
  lcd.print(((str((env1.temperature)) + str('°C  '))), 14, (margin_top + 22), 0xffffff)
  if (env1.temperature) < 17 or (env1.temperature) > 28:
    temperature.setBgColor(0xff0000)
  else:
    temperature.setBgColor(0x33ff33)
  lcd.print(((str((env1.humidity)) + str('%  '))), 14, (margin_top + 38), 0xffffff)
  if (env1.humidity) < 30 or (env1.humidity) > 60:
    humidity.setBgColor(0xff0000)
  else:
    humidity.setBgColor(0x33ff33)
  lcd.print(((str('0') + str('%'))), 14, (margin_top + 82), 0xffffff)
  lcd.print(((str(round((earth1.analogValue) * 100 / 1024)) + str('%  '))), 178, 86, 0xffffff)
  lcd.print(((str(round((earth2.analogValue) * 100 / 1024)) + str('%  '))), 178, 70, 0xffffff)
  if round((earth1.analogValue) * 100 / 1024) < 30:
    level1.setBgColor(0xff9900)
  else:
    level1.setBgColor(0x33ff33)
  if round((earth2.analogValue) * 100 / 1024) < 30:
    level2.setBgColor(0xff9900)
  else:
    level2.setBgColor(0x33ff33)
  lcd.print(((str((power.getBatteryLevel())) + str('%  '))), 184, 128, 0xffffff)
  if i == 0 or i % 19 == 0:
    if wifiCfg.wlan_sta.isconnected():
      try:
        req = urequests.request(method='GET', url=(str('http://emoncms.org/input/post?node=M5Stack-gray2&apikey=<your_api_key>&fulljson=') + str(((str(((str('{"temperature":') + str((env1.temperature))))) + str(((str(',"humidity":') + str(((str((env1.humidity)) + str(((str(((str(',"soil0":') + str(((str(((earth1.analogValue) * 100 / 1024)) + str(((str(',"soil1":') + str(((earth2.analogValue) * 100 / 1024))))))))))) + str(((str(',"battery":') + str(((str((power.getBatteryLevel())) + str('}')))))))))))))))))))))
        rgb.setBrightness(100)
        rgb.setColorAll(0x33ff33)
        wait(1)
        rgb.setBrightness(0)
        rgb.setColorAll(0x000000)
      except:
        rgb.setBrightness(100)
        rgb.setColorAll(0xff0000)
        wait(1)
        rgb.setBrightness(0)
        rgb.setColorAll(0x000000)
      try:
        req = urequests.request(method='GET', url='http://nodered.lenuage.io/watering')
        watering_frequency = (json.loads((req.text)))['watering_frequency']
        watering_duration = (json.loads((req.text)))['watering_duration']
        lcd.print(((str('0') + str(((str('% ') + str(((str((watering_duration / 60)) + str(((str('/') + str((watering_frequency / 3600))))))))))))), 14, (margin_top + 82), 0xffffff)
        rgb.setBrightness(100)
        rgb.setColorAll(0x33ff33)
        wait(1)
        rgb.setBrightness(0)
        rgb.setColorAll(0x000000)
      except:
        rgb.setBrightness(100)
        rgb.setColorAll(0xff0000)
        wait(1)
        rgb.setBrightness(0)
        rgb.setColorAll(0x000000)
    else:
      pass
  if (i == 0 or i > watering_frequency / 30) and ((earth1.analogValue) * 100 / 1024) <= 50 and ((earth2.analogValue) * 100 / 1024) <= 50:
    if wifiCfg.wlan_sta.isconnected():
      relay1.on()
      wait(watering_duration)
      relay1.off()
      wait(1)
      try:
        req = urequests.request(method='GET', url=(str('http://emoncms.org/input/post?node=M5Stack-gray2&apikey=apikey=<your_api_key>&fulljson=') + str('{"pump":1}')))
        rgb.setBrightness(100)
        rgb.setColorAll(0x33ff33)
        wait(1)
        rgb.setBrightness(0)
        rgb.setColorAll(0x000000)
      except:
        rgb.setBrightness(100)
        rgb.setColorAll(0xff0000)
        wait(1)
        rgb.setBrightness(0)
        rgb.setColorAll(0x000000)
    else:
      pass
    i = 1
  wait(30)
  i = (i if isinstance(i, Number) else 0) + 1
  screen_is_on = False
  lcd.setBrightness(0)
  lcd.clear()
  wait_ms(2)
