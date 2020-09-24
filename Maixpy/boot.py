# 主程序

import lcd, time, image, sensor, network, socket, json
from Maix import GPIO
from fpioa_manager import fm
from Machine import UART

WIFI_SSID = 'ESP8266'
WIFI_PASSWD = '43214321a'

lcd.init(freq=1500000)

# show hxcl logo after reset
lcd.clear(lcd.BLACK)
time.sleep(1)
img = img.Image('/sd/hxcl_logo.jpg')
lcd.display(img)
time.sleep(3)

lcd.clear(lcd.BALCK)

# LCD 初始化成功
lcd.draw_string(10,10,"LCD init ... successfully!",lcd.WHITE,lcd.BLACK)

# 初始化摄像头
lcd.draw_string(10,10,"Camera init ... ",lcd.WHITE,lcd.BLACK)
try:
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.run(1)
except:
    lcd.draw_string(, , "failed! Please check", lcd.WHITE, lcd.BLACK)
else:
    lcd.draw_string(, , "siccessfully!", lcd.WHITE, lcd.BLACK)

# 初始化 ESP32 
lcd.draw_string(10,10,"WiFi init ... ",lcd.WHITE,lcd.BLACK)
fm.register(25,fm.fpioa.GPIOHS10)#cs
fm.register(8,fm.fpioa.GPIOHS11)#rst
fm.register(9,fm.fpioa.GPIOHS12)#rdy
fm.register(28,fm.fpioa.GPIOHS13)#mosi
fm.register(26,fm.fpioa.GPIOHS14)#miso
fm.register(27,fm.fpioa.GPIOHS15)#sclk
nic = network.ESP32_SPI(cs=fm.fpioa.GPIOHS10,rst=fm.fpioa.GPIOHS11,rdy=fm.fpioa.GPIOHS12, mosi=fm.fpioa.GPIOHS13,miso=fm.fpioa.GPIOHS14,sclk=fm.fpioa.GPIOHS15)

if not nic:
    nic = network.ESP32_SPI(cs=fm.fpioa.GPIOHS10,rst=fm.fpioa.GPIOHS11,rdy=fm.fpioa.GPIOHS12, mosi=fm.fpioa.GPIOHS13,miso=fm.fpioa.GPIOHS14,sclk=fm.fpioa.GPIOHS15)
    continue
if not nic.isconnected():
    print("connect WiFi now")
    try:
        err = 0
        while 1:
            try:
                nic.connect(WIFI_SSID, WIFI_PASSWD)
            except Exception:
                err += 1
                print("Connect AP failed, now try again")
                if err > 3:
                    raise Exception("Conenct AP fail")
                continue
            break
        nic.ifconfig()
    except Exception:
        continue
if not nic.isconnected():
    print("WiFi connect fail")
    continue

# 初始化 Air530
lcd.draw_string(10,10,"GNSS init ... successfully!",lcd.WHITE,lcd.BLACK)

# 初始化 KPU 与模型
lcd.draw_string(10,10,"KPU init ... successfully!",lcd.WHITE,lcd.BLACK)

# 进入主程序的入口
fm.register(17, fm.fpioa.GPIOHS1, force=True)
key0 = GPIO(GPIO.GPIOHS1, GPIO.IN)
lcd.draw_string( , , "Plase press key0 to start road condition detetion")

while(input!=1):
    time.sleep_ms(1)

