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
    # Key0
fm.register(17, fm.fpioa.GPIOHS1, force=True)

uart1 = UART(UART.UART1, 9600,8,0,0,timeout=1000,read_buf_len=2048)
GNSS = Air530(uart1)
# 初始化
init()

# 按下按钮，开始检测程序
key0 = GPIO(GPIO.GPIOHS1, GPIO.IN)
lcd.draw_string( , , "Plase press key0 to start road condition detetion")

while(input!=1):
    time.sleep_ms(1)

# 
# 在检测程序里面，将进行获取图像-检测-发送图像的循环。同时会有定时器任务更新 GPS 数据

# 定时刷新定位信息
def GNSS_info_update(timer):
    GNSS.GNSS_Read()
    GNSS.GNSS_Parese()
    lcd.draw_string(0,40,"Date: "+GNSS.date,lcd.BLACK,lcd.WHITE)
    lcd.draw_string(0,60,"UTC Time: "+GNSS.UTC_Time,lcd.BLACK,lcd.WHITE)
    lcd.draw_string(0,80,"latitude:  "+GNSS.latitude+GNSS.N_S,lcd.BLACK,lcd.WHITE)
    lcd.draw_string(0,100,"longitude: "+GNSS.longitude+GNSS.E_W,lcd.BLACK,lcd.WHITE)
    lcd.draw_string(0,120,"Speed: "+str(GNSS.speed_to_groud_kh)+"km/h",lcd.BLACK,lcd.WHITE)
    lcd.draw_string(0,140,"Course_over_ground: "+str(GNSS.course_over_ground),lcd.BLACK,lcd.WHITE)
    GNSS.print_GNSS_info()

tim = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PERIODIC, period=3000, callback=GNSS_info_update)
tim.start()

while True:
    # 用于生成图片名的计数器
    img_number = 0

    img = sensor.snapshot()
    code = kpu.run(task, img)
    # 此处考虑加入根据置信度判断

    if code:
        for i in code:
            print(i)
            img.draw_retangle(i.rect())
            for i in code:
                lcd.draw_string(i.x(), i.y(), classes[i.classid()], lcd.RED, lcd.WHITE)
                lcd.draw_string(i.x(), i.y()+12, '%.3f'%i.value(), lcd.RED, lcd.WHITE)
    else:
        pass

    if GNSS.DataIsUseful == False:
        img.draw_string(0, 0, "GNSS is not useful!", lcd.RED, lcd.WHITE)
        lcd.display(img)
    else:
        lcd.display(img)
        
        # json 
        GNSS_data = [
            {
                'client_number' : client_number,
                'latitude' : GNSS.latitude,
                'longtitude' : GNSS.longitude,
                'date' : GNSS.date,
                'UTC_Time' : GNSS.UTC_Time,
                'pic_name' : GNSS.UTC_Time + '-' + str(img_number)
            }
        ]
        
        img_number += 1
        if img_number > 999
            img_number = 0

        json_str = json.dumps(GNSS_data)
        send_len = sock.sendall(json_str)

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
