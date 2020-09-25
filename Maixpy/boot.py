# 主程序


import lcd, time, image, sensor, network, socket, json
from Maix import GPIO
from fpioa_manager import fm
from Machine import UART, Timer
import init
from Air530 import Air530

# 常量定义
WIFI_SSID = 'ESP8266'
WIFI_PASSWD = '43214321a'

# YOLO 类别
classes = []

# client 编号
client_number = 0

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

# 初始化
init()

# 按下按钮，开始检测程序
fm.register(17, fm.fpioa.GPIOHS1, force=True)
key0 = GPIO(GPIO.GPIOHS1, GPIO.IN)
lcd.draw_string( , , "Plase press key0 to start road condition detetion")

while(input!=1):
    time.sleep_ms(1)

# 
# 在检测程序里面，将进行获取图像-检测-发送图像的循环。同时会有定时器任务更新 GPS 数据

while True:
    img = sensor.snapshot()
    code = kpu.run(task, img)
    # 此处考虑加入根据置信度判断

    if code:
        for i in code:
            print(i)
            img.draw_retangle(i.rect())
            for i in code:
                lcd.draw_string(i.x(), i.y(), classes[i.classid()], lcd.RED, lcd.WHITE)
                lcd.draw_string(i.x(), i.y()+12, '%。3f'%i.value(), lcd.RED, lcd.WHITE)
    else:
        pass

    if == False:
        img.draw_string(0, 0, "GNSS is not useful!", lcd.RED, lcd.WHITE)
        lcd.display(img)
    else:
        lcd.display(img)
        
        # json 相关，待处理


        # socket 发送图片
        img = img.compress(quality=60)
        img_bytes = img.to_bytes()
        print("send len: ", len(img_bytes))
        try:
            block = int(len(img_bytes)/2048)
            for i in range(block):
                send_len = sock.send(img_bytes[i*2048:(i+1)*2048])
                #time.sleep_ms(500)
            send_len2 = sock.send(img_bytes[block*2048:])
            #send_len = sock.send(img_bytes[0:2048])
            #send_len = sock.send(img_bytes[2048:])
            #time.sleep_ms(500)
            if send_len == 0:
                raise Exception("send fail")
        except OSError as e:
            if e.args[0] == 128:
                print("connection closed")
                break
        except Exception as e:
            print("send fail:", e)
            time.sleep(1)
            err += 1
            continue
        count += 1
        print("send:", count)
        sock.close()
