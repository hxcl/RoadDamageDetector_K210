from machine import I2C

MLX90614_I2CADDR = 0x00

# RAM
MLX90614_RAWIR1 = 0x04
MLX90614_RAWIR2 = 0x05
MLX90614_TA = 0x06
MLX90614_TOBJ1 = 0x07
MLX90614_TOBJ2 = 0x08
# EEPROM
MLX90614_TOMAX = 0x20
MLX90614_TOMIN = 0x21
MLX90614_PWMCTRL = 0x22
MLX90614_TARANGE = 0x23
MLX90614_EMISS = 0x24
MLX90614_CONFIG = 0x25
MLX90614_ADDR = 0x0E
MLX90614_ID1 = 0x3C
MLX90614_ID2 = 0x3D
MLX90614_ID3 = 0x3E
MLX90614_ID4 = 0x3F

class MLX90614():
    def __init__(self, i2c_port):
        self.__i2c_addr = MLX90614_I2CADDR
        self.__i2c_port = i2c_port
        self.ObjectTempC = 0
        self.AmbinetTempC = 0

    # 从寄存器地址读取指定的字节数
    def read(self, register, n):
        templist = self.__i2c_port.readfrom_mem(self.__i2c_addr, register, n, mem_size=8)
        
        return templist

    def readTemp(self, register):
        templist = self.read(MLX90614_TOBJ1, 3)
        temp = float(templist[1]*256+templist[0])
        temp *= 0.02
        temp -= 273.15
        return temp

    # 背景摄氏温度
    def readAmbientTempC(self):
        self.AmbinetTempC = self.readTemp(MLX90614_TA)
        return self.AmbinetTempC

    # 物体摄氏温度
    def readObjectTempC(self):
        self.ObjectTempC = self.readTemp(MLX90614_TOBJ1)
        return self.ObjectTempC