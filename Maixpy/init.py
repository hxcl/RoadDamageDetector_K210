# 上电初始化部分
# 上电以后可以搞点看起来比较牛逼的效果，我目前设计的是先展示 logo 
# 再依次显示各功能模块的初始化
# 后期还可以添加

import lcd, time, image, sensor, network
from Maix import GPIO
from fpioa_manager import fm
from Machine import UART

def init():
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
        lcd.draw_string(, , "successfully!", lcd.WHITE, lcd.BLACK)

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
    task = kpu.load()