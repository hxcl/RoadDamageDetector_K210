from machine import UART
from fpioa_manager import fm
import video
import sensor, image, lcd, time
from ADXL345_ATmode import Ace
import ujson
import network

lcd.init()
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.run(1)

fm.register(34, fm.fpioa.UART1_TX, force = True)
fm.register(35, fm.fpioa.UART1_RX, force = True)

uart1 = UART(UART.UART1, 115200, 8, 0, 0, timeout=1000, read_buf_len=128)

ace = Ace(uart1)
ace.ace_init()

recore = video.open("/sd/%s"%name,record = True)
record.volume(50)
while True:
    ace.read_ace()
    if (ace.ax^2 + ace.ay^2 + ace.az^2) > 10000000:
        dict = {
            'name':'ASD',
            'ax':ace.ax,
            'ay':ace.ay,
            'az':ace.az
        }

    json_str = ujson.dumps(dict)
    print(json_str)

    if v.play() == 0:
        print("play end")
        break
