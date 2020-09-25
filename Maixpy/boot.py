# 主程序


import lcd, time, image, sensor, network, socket, json
from Maix import GPIO
from fpioa_manager import fm
from Machine import UART

# 常量定义
WIFI_SSID = 'ESP8266'
WIFI_PASSWD = '43214321a'

# 引脚分配
    # Air230 相关
fm.register(34, fm.fpioa.UART1_TX, force = True)
fm.register(35, fm.fpioa.UART1_RX, force = True)
    # ESP32 相关
fm.register(25, fm.fpioa.GPIOHS10, force = True)#cs
fm.register(8, fm.fpioa.GPIOHS11, force = True)#rst
fm.register(9, fm.fpioa.GPIOHS12, force = True)#rdy
fm.register(28, fm.fpioa.GPIOHS13, force = True)#mosi
fm.register(26, fm.fpioa.GPIOHS14, force = True)#miso
fm.register(27, fm.fpioa.GPIOHS15, force = True)#sclk


# 上电初始化部分
# 上电以后可以搞点看起来比较牛逼的效果，我目前设计的是先展示 logo 
# 再依次显示各功能模块的初始化
# 后期还可以添加

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

# 按下按钮，开始检测程序
fm.register(17, fm.fpioa.GPIOHS1, force=True)
key0 = GPIO(GPIO.GPIOHS1, GPIO.IN)
lcd.draw_string( , , "Plase press key0 to start road condition detetion")

while(input!=1):
    time.sleep_ms(1)

# 
# 在检测程序里面，将进行获取图像-检测-发送图像的循环。同时会有定时器任务更新 GPS 数据