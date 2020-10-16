# 主程序

import lcd, time, image, sensor, network, socket, json, gc
import KPU as kpu
from fpioa_manager import fm
from Maix import GPIO
from machine import UART, Timer, I2C, reset

from Air530 import Air530
from ADXL345_ATmode import Ace
from MLX90614 import MLX90614

# 功能切换变量
GLOBAL_STATE = 1

# 网络参数
####################################################################
WIFI_SSID = '123456'
WIFI_PASSWD = '43214321a'
server_ip = "192.168.43.93"
server_port = 3456
####################################################################

# 客户机编号
####################################################################
client_number = 0
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

# 三色 LED ws2812
####################################################################
color_Blank = (0, 0, 0)
color_R = (255, 0, 0)
color_G = (0, 255, 0)
color_B = (0, 0, 255)
color_Yellow = (255, 255, 0)

LED_BLANK = 0
LED_RED = 1
LED_GREEN = 2
LED_YELLOW = 3

LED_state = 0
####################################################################

MASKED = 1
NOTMASKED = 0

uart1 = UART(UART.UART1, 9600,8,0,0,timeout=1000,read_buf_len=2048)
GNSS = Air530(uart1)

# 展示 Logo 与介绍信息
lcd.init(freq=1500000)
lcd.clear(lcd.BLACK)
lcd.rotation(1)
#img = image.Image('/flash/hxcl_logo.jpg')
#lcd.display(img)
#time.sleep(1)

# ESP32 连接 WiFi
network = network.ESP32_SPI(cs=fm.fpioa.GPIOHS10,rst=fm.fpioa.GPIOHS11, rdy=fm.fpioa.GPIOHS12, mosi=fm.fpioa.GPIOHS13, miso=fm.fpioa.GPIOHS14, sclk=fm.fpioa.GPIOHS15)
addr = (server_ip, server_port)
if not network.isconnected():
    print("connect WiFi now")
    try:
        err = 0
        while 1:
            try:
                network.connect(WIFI_SSID, WIFI_PASSWD)
            except Exception:
                err += 1
                print("Connect AP failed, now try again")
                if err > 1:
                    raise Exception("Conenct AP fail")
                continue
            break
        network.ifconfig()
    except Exception:
        pass
if not network.isconnected():
    print("WiFi connect fail")

# 定时器回调刷新定位信息
def GNSS_info_update(timer):
    GNSS.GNSS_Read()
    GNSS.GNSS_Parese()
    GNSS.print_GNSS_info()

tim = Timer(Timer.TIMER0, Timer.CHANNEL0, mode=Timer.MODE_PERIODIC, period=3000, callback=GNSS_info_update)
tim.stop()

# 按钮触发中断，回调函数判断当前状态
def key_irq(pin_num):
    global GLOBAL_STATE
    print("IRQ:%d"%GLOBAL_STATE)
    if GLOBAL_STATE == 0:
        GLOBAL_STATE = 1
    elif GLOBAL_STATE == 1:
        GLOBAL_STATE = 2
    elif GLOBAL_STATE == 2:
        GLOBAL_STATE = 1
    else:
        reset()

key = GPIO(GPIO.GPIOHS1, GPIO.IN, GPIO.PULL_DOWN)
key.irq(key_irq, GPIO.IRQ_RISING, GPIO.WAKEUP_NOT_SUPPORT, 7)


def drawConfidenceText(image, rol, classid, value, color):
    text = ""
    _confidence = int(value * 100)

    if classid == MASKED:
        text = 'mask: ' + str(_confidence) + '%'
    else:
        text = 'no_mask: ' + str(_confidence) + '%'

    image.draw_string(rol[0], rol[1], text, color=color, scale=2.5)

def LED_update():
    if LED_state == LED_BLANK:
        LED.set_led(0, LED_BLANK)
    elif LED_state == LED_RED:
        LED.set_led(0, LED_RED)
    elif LED_state == LED_YELLOW:
        LED.set_led(0, LED_YELLOW)
    elif LED_state == LED_GREEN:
        LED.set_led(0, LED_GREEN)

    LED.display()


# 在下面这个大死循环里面，有路面检测和口罩识别两个任务的死循环
# 两个任务的一次循环最后，都会判断一次全局变量 GLOBAL_STATE，以决定是否跳出，也就是切换任务
# 全局变量 GLOBAL_STATE 在按键中断中修改
while True:

    sensor.reset(dual_buf=True)
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_windowing((224, 224))
    sensor.set_brightness(2)
    sensor.run(1)

    sock = socket.socket()
    print(sock)


    # YOLO 类别
    classes = ["D00","D01","D10","D11","D20","D40","D43","D44"]

    #task = kpu.load("/sd/road_yolov2_new_anchor.kmodel")
    #task = kpu.load("/sd/road_yolov2.kmodel")
    task = kpu.load(0x500000)
    anchor = (0.37, 0.51, 0.78, 0.9, 1.0, 1.09, 1.13, 2.22, 5.33, 5.95)
    a = kpu.init_yolo2(task, 0.17, 0.3, 5, anchor)


    # 在路面检测程序里面，将进行获取图像-检测-发送图像的循环。同时会有定时器任务更新 GPS 数据
    # 路面检测需要使用 GPS 因此启动定时器
    GNSS.GNSS_Read()
    GNSS.GNSS_Parese()
    #GNSS.print_GNSS_info()

    GNSS.DataIsUseful = True

    #tim.start()

    clock = time.clock()

    while True:
        #print("task 1 start")

        count = 0
        err   = 0

        clock.tick()

        img = sensor.snapshot()
        code = kpu.run_yolo2(task, img)
        #print(clock.fps())

        img.draw_string(0,0, "LAT: "+GNSS.latitude+GNSS.N_S, color=color_R, scale = 1.0)
        img.draw_string(0,16, "LON: "+GNSS.longitude+GNSS.E_W, color=color_R, scale = 1.0)
        img.draw_string(0,32, "Speed: "+str(GNSS.speed_to_groud_kh)+"km/h",color=color_R, scale = 1.0)

        if GNSS.DataIsUseful == False:
            img.draw_string(120, 0, "GPS is not useful", color=color_R, scale = 1.0)

        if code:
            for i in code:
                print(i)
                img.draw_rectangle(i.rect())
            for i in code:
                lcd.draw_string(i.x(), i.y(), classes[i.classid()], lcd.RED, lcd.WHITE)
                lcd.draw_string(i.x(), i.y()+12, '%.3f'%i.value(), lcd.RED, lcd.WHITE)
            if GNSS.DataIsUseful == False:
                print("GNSS is not useful")
                lcd.display(img)
            else:
                lcd.display(img)


                # socket 发送图片和图片信息
                try:
                    sock.connect(addr)
                except Exception as e:
                    print("connect error:", e)
                    sock.close()
                    continue
                sock.settimeout(5)

                img = img.compress(quality=50)
                img_bytes = img.to_bytes()
                print("now sending the image")

                GNSS_data = [
                    {
                        'client_number' : client_number,
                        'latitude' : GNSS.latitude,
                        'longtitude' : GNSS.longitude,
                        'date' : GNSS.date,
                        'UTC_Time' : GNSS.UTC_Time,
                    }
                ]
                json_str = json.dumps(GNSS_data)
                json_str = "\r\r\r\r" + json_str

                json_bytes = json_str.encode("ASCII")

                img_bytes = img_bytes + json_bytes

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
                print("sock close")

        else:
            lcd.display(img)

        #global GLOBAL_STATE
        if GLOBAL_STATE == 2:
            kpu.deinit(task)
            ROAD_CONDITION_INIT = 0
            print("breaking road detect task")
            break


        # 口罩检测无需 GPS ，因此停止定时器避免打断
    tim.stop()

    class_IDs = ['no_mask', 'mask']

    IR_sensor_i2c = I2C(I2C.I2C0, freq=100000, scl=32, sda=33)
    devices = IR_sensor_i2c.scan()
    IR_sensor = MLX90614(IR_sensor_i2c)

    sensor.reset(dual_buff=True)
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.set_hmirror(0)
    sensor.run(1)

    task = kpu.load(0x800000)
    #task = kpu.load("/sd/mask.kmodel")

    anchor = (0.1606, 0.3562, 0.4712, 0.9568, 0.9877, 1.9108, 1.8761, 3.5310, 3.4423, 5.6823)
    _ = kpu.init_yolo2(task, 0.5, 0.3, 5, anchor)
    img_lcd = image.Image()

    clock = time.clock()

    while (True):
        clock.tick()
        img = sensor.snapshot()
        code = kpu.run_yolo2(task, img)

        if code:
            totalRes = len(code)
            LED_state = LED_GREEN

            for item in code:
                confidence = float(item.value())
                itemROL = item.rect()
                classID = int(item.classid())

                if classID == NOTMASKED:
                    LED_state = LED_YELLOW

                if confidence < 0.52:
                    _ = img.draw_rectangle(itemROL, color=color_B, tickness=5)
                    continue

                if classID == MASKED and confidence > 0.65:
                    _ = img.draw_rectangle(itemROL, color_G, tickness=5)
                    if totalRes == 1:
                        drawConfidenceText(img, (40, 0), 1, confidence, color_G)
                else:
                    _ = img.draw_rectangle(itemROL, color=color_R, tickness=5)
                    if totalRes == 1:
                        drawConfidenceText(img, (40, 0), 0, confidence, color_R)

            IR_temp = IR_sensor.readObjectTempC() + 2.5

            print(IR_temp)
            if IR_temp > 37.5:
                LED_state = LED_RED

                img.draw_string(230, 0, str(IR_temp), color = color_R, scale = 2.5)
            else:
                img.draw_string(230, 0, str(IR_temp), color = color_G, scale = 2.5)

        else:
            LED_state = LED_BLANK

        _ = lcd.display(img)
        print(clock.fps())
        if GLOBAL_STATE == 1:
            kpu.deinit(task)
            break
