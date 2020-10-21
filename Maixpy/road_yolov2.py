
import sensor, image, lcd, time, network, socket, json
from fpioa_manager import fm
from Maix import GPIO
from machine import UART
import KPU as kpu

from Air530 import Air530

# 网络参数
####################################################################
WIFI_SSID = 'ESP8266'
WIFI_PASSWD = '43214321a'
server_ip = "192.168.1.1"
server_port = 3456
####################################################################

# 引脚分配
####################################################################
    # Air530
fm.register(0, fm.fpioa.UART1_TX, force = True)
fm.register(1, fm.fpioa.UART1_RX, force = True)
    # ESP32
fm.register(25, fm.fpioa.GPIOHS10, force = True)#cs
fm.register(8, fm.fpioa.GPIOHS11, force = True)#rst
fm.register(9, fm.fpioa.GPIOHS12, force = True)#rdy
fm.register(28, fm.fpioa.GPIOHS13, force = True)#mosi
fm.register(26, fm.fpioa.GPIOHS14, force = True)#miso
fm.register(27, fm.fpioa.GPIOHS15, force = True)#sclk
    # Key
fm.register(35, fm.fpioa.GPIOHS1, force=True)
####################################################################

uart1 = UART(UART.UART1, 9600,8,0,0,timeout=1000,read_buf_len=2048)
GNSS = Air530(uart1)

lcd.init(freq=15000000)
sensor.reset(dual_buf=False)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
#sensor.set_hmirror(1)
#sensor.set_vflip(1)
sensor.set_windowing((224, 224))
sensor.set_brightness(2)
#sensor.set_contrast(-1)
#sensor.set_auto_gain(1,2)

sensor.run(1)
clock = time.clock()
classes = ["D00","D01","D10","D11","D20","D40","D43","D44"]
task = kpu.load(0x500000)
#anchor = (1, 1.2, 2, 3, 4, 3, 6, 4, 5, 6.5)
anchor = (0.37, 0.51, 0.78, 0.9, 1.0, 1.09, 1.13, 2.22, 5.33, 5.95)
a = kpu.init_yolo2(task, 0.17, 0.3, 5, anchor)
while(True):
    clock.tick()
    img = sensor.snapshot()
    code = kpu.run_yolo2(task, img)
    print(clock.fps())
    if code:
        for i in code:
            a=img.draw_rectangle(i.rect())
            a = lcd.display(img)
            print(i.classid(),i.value())
            for i in code:
                lcd.draw_string(i.x(), i.y(), classes[i.classid()], lcd.RED, lcd.WHITE)
                lcd.draw_string(i.x(), i.y()+12, '%f1.3'%i.value(), lcd.RED, lcd.WHITE)
    else:
        a = lcd.display(img)
a = kpu.deinit(task)
