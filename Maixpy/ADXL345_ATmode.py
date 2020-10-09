from fpioa_manager import fm
from machine import UART
import utime

class Ace():
    def __init__(self, uart_port, ms=1000):
        self.__uart_port = uart_port
        self.is_inited = False
        self.frequency_ms = ms
        self.buffer = ""
        self.ax = 0
        self.ay = 0
        self.az = 0

    def ace_init(self):
        self.__uart_port.write("AT+INIT\r\n")
        temp = self.__uart_port.read(16)
        if temp == "INIT SUCCESS":
            self.is_inited = True
            print("ace init successfully")
        else:
            self.is_inited = False
            print("ace init fail")

    # ms = 0 为单次回传模式，直接调用 read_ace() 即可，无需设置频率
    # ms 为其他数值表示每若干毫秒发送一次数据
    def ace_set_frequency(self, ms):
        if (ms<10 or ms>10000):
            print("frequency out of range")
        
        self.__uart_port.write("AT+PRATE=%d\r\n" % ms)
        temp = self.__uart_port.read(16)
        if temp == "OK":
            print("Set frequency success")
        else:
            print("Set frequency failed")

    # 仅用于单次回传模式
    def read_ace(self):
        self.__uart_port.write("AT+PRATE=0\r\n")
        self.buffer = self.__uart_port.read(200)
        ax_head = self.buffer.find("AX=")
        ay_head = self.buffer.find("AY=")
        az_head = self.buffer.find("AZ=")
        
        self.ax = int(self.buffer[ax_head+3:ax_head+5])
        self.ay = int(self.buffer[ay_head+3:ay_head+5])
        self.az = int(self.buffer[az_head+3:az_head+5])