from fpioa_manager import fm
from machine import UART
import utime

# 维特智能模块 AT 模式

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
        send_init = False
        while send_init == False:
            try:
                self.__uart_port.write("AT+INIT\r\n")
                temp = self.__uart_port.read(32)
                temp = temp.decode("ASCII")
            except UnicodeError:
                pass
            else:
                send_init = True

        if temp.find("INIT SUCCESS\r\n") != -1:
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

        send_init = False
        while send_init == False:
            try:
                self.__uart_port.write("AT+PRATE=%d\r\n" % ms)
                temp = self.__uart_port.read(16)
                temp = temp.decode("ASCII")
            except UnicodeError:
                pass
            else:
                send_init = True

        if temp == "OK":
            print("Set frequency success")
        else:
            print("Set frequency failed")

    # 仅用于单次回传模式
    def read_ace(self):
        send_init = False
        while send_init == False:
            try:
                self.__uart_port.write("AT+PRATE=0\r\n")
                self.buffer = self.__uart_port.read(64)
                self.buffer = self.buffer.decode('ASCII')
            except UnicodeError:
                pass
            else:
                send_init = True

        print(self.buffer)

        ax_head = self.buffer.find("AX=")
        ax_tail = self.buffer[ax_head:].find("mg")
        ay_head = self.buffer.find("AY=")
        ay_tail = self.buffer[ay_head:].find("mg")
        az_head = self.buffer.find("AZ=")
        az_tail = self.buffer[az_head:].find("mg")

        self.ax = int(self.buffer[ax_head+3:ax_head + ax_tail])
        self.ay = int(self.buffer[ay_head+3:ay_head + ay_tail])
        self.az = int(self.buffer[az_head+3:az_head + az_tail])


if __name__ == "__main__":
    fm.register(34, fm.fpioa.UART1_TX, force = True)
    fm.register(35, fm.fpioa.UART1_RX, force = True)

    uart1 = UART(UART.UART1, 115200, 8, 0, 0, timeout=1000, read_buf_len=128)

    ace = Ace(uart1)
    ace.ace_init()
    ace.read_ace()
    print(ace.ax)
    print(ace.ay)
    print(ace.az)