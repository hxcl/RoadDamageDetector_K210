# thanks to [理工小白](https://me.csdn.net/qq_42431739) about the face and mask detecitons
# https://blog.csdn.net/qq_42431739/article/details/106102805

# 人体测温和口罩识别

import sensor, image, lcd, time
import KPU as kpu
from Maix import GPIO
from fpioa_manager import fm
from machine import I2C
from MLX90614 import MLX90614
from modules import ws2812

color_Blank = (0, 0, 0)
color_R = (255, 0, 0)
color_G = (0, 255, 0)
color_B = (0, 0, 255)
color_Yellow = (255, 255, 0)

# MAIX GO 三色 LED
##########################################################
fm.register(14, fm.fpioa.GPIOHS0, force=True)
fm.register(13, fm.fpioa.GPIOHS1, force=True)
fm.register(12, fm.fpioa.GPIOHS2, force=True)

led_r = GPIO(GPIO.GPIOHS0, GPIO.OUT)
led_g = GPIO(GPIO.GPIOHS1, GPIO.OUT)
led_b = GPIO(GPIO.GPIOHS2, GPIO.OUT)

led_r.value(0)
led_g.value(0)
led_b.value(0)
###########################################################

# 智-识 WS2812
###########################################################
LED = ws2812(34, 1)
###########################################################

LED_BLANK = 0
LED_RED = 1
LED_GREEN = 2
LED_YELLOW = 3

LED_state = 0

class_IDs = ['no_mask', 'mask']
MASKED = 1
NOTMASKED = 0

IR_sensor_i2c = I2C(I2C.I2C0, freq=100000, scl=32, sda=33)
devices = IR_sensor_i2c.scan()
IR_sensor = MLX90614(IR_sensor_i2c)

def drawConfidenceText(image, rol, classid, value):
    text = ""
    _confidence = int(value * 100)

    if classid == MASKED:
        text = 'mask: ' + str(_confidence) + '%'
    else:
        text = 'no_mask: ' + str(_confidence) + '%'

    image.draw_string(rol[0], rol[1], text, color=color_R, scale=2.5)

def LED_update():
    # MAIX GO
    ########################################
    # if LED_state == LED_BLANK:
    #     led_r.value(1)
    #     led_g.value(1)
    #     led_b.value(1)
    # elif LED_state == LED_RED:
    #     led_r.value(0)
    #     led_g.value(1)
    #     led_b.value(1)
    # elif LED_state == LED_YELLOW:
    #     led_r.value(0)
    #     led_g.value(0)
    #     led_b.value(1)
    # elif LED_state == LED_GREEN:
    #     led_r.value(1)
    #     led_g.value(0)
    #     led_b.value(1)
    #######################################

    # WS2812
    #######################################
    if LED_state == LED_BLANK:
        LED.set_led(0, LED_BLANK)
    elif LED_state == LED_RED:
        LED.set_led(0, LED_RED)
    elif LED_state == LED_YELLOW:
        LED.set_led(0, LED_YELLOW)
    elif LED_state == LED_GREEN:
        LED.set_led(0, LED_GREEN)
    #######################################


lcd.init()
lcd.rotation(1)
sensor.reset(freq=24000000,dual_buf=True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_hmirror(0)
sensor.run(1)

#task = kpu.load(0x500000)
task = kpu.load("/sd/mask.kmodel")

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
                    drawConfidenceText(img, (0, 0), 1, confidence)
            else:
                _ = img.draw_rectangle(itemROL, color=color_R, tickness=5)
                if totalRes == 1:
                    drawConfidenceText(img, (0, 0), 0, confidence)

        #IR_temp = IR_sensor.readObjectTempC()

        #print(IR_temp)
        #if IR_temp > 37.5:
            #LED_state = LED_RED

        #img.draw_string(230, 0, str(IR_temp), color=color_R, scale=2.5)

    else:
        LED_state = LED_BLANK

    LED_update()

    _ = lcd.display(img)

    print(clock.fps())

_ = kpu.deinit(task)
