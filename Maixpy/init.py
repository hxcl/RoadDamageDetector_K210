import lcd, time, image

def init():
    lcd.init(freq=1500000)

    # show hxcl logo after reset
    lcd.clear(lcd.BLACK)
    time.sleep(1)
    img = image.Image('/sd/hxcl_logo1.jpg')
    lcd.display(img)
    time.sleep(2)
    img = image.Image('/sd/introduction.jpg')
    lcd.display(img)

if __name__ == "__main__":
    init()
