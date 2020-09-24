# 本脚本用于测试本团队自行设计的硬件，整个脚本分为四部分，分别对应了硬件四个功能模块
# 本脚本仅限测试硬件使用，未经修改无法在其他开发板上使用

# 第一部分 - 电源、ISP、摄像头，应首先完成上述部分的焊接并测试固件烧录
import sensor, image, time

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framsize(sensor.QVGA)
sensor.run(1)

while True:
    pirnt("Hello world!")
    time.sleep(1)

# 第二部分 - Air530 模组，应首先完成相关部分元件的焊接
from Maix import GPIO
from fpioa_manager import fm
from machine import UART

fm.register(34, fm.fpioa.UART1_TX, force = True)
fm.register(35, fm.fpioa.UART1_RX, force = True)

GNSS_uart = UART(UART.UART, 9600, 8, 0, 0, timeout = 100, read_buf_len = 1024)

GNSS_data = GNSS_uart.read()
if GNSS_data:
    GNSS_str = GNSS_data.decode('ASCII')
    print(GNSS_str)

time_sleep(2)

# 第三部分 - ESP32 模组，应首先完成相关部分元件的焊接，并测试 ESP32 固件烧录
import network, socket

WIFI_SSID = 'ESP8266'
WIFI_PASSWD = '43214321a'

fm.register(25,fm.fpioa.GPIOHS10)#cs
fm.register(8,fm.fpioa.GPIOHS11)#rst
fm.register(9,fm.fpioa.GPIOHS12)#rdy
fm.register(28,fm.fpioa.GPIOHS13)#mosi
fm.register(26,fm.fpioa.GPIOHS14)#miso
fm.register(27,fm.fpioa.GPIOHS15)#sclk



while True:
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

# 第四部分 - LCD 与 TF 卡，这个直接用录像的例程就好了