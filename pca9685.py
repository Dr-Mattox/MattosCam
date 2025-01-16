# pca9685.py

import time
from machine import I2C

_MODE1       = 0x00
_PRESCALE    = 0xFE
_LED0_ON_L   = 0x06

class PCA9685:
    def __init__(self, i2c, address=0x40):
        self.i2c = i2c
        self.address = address
        # Configurar modo inicial
        self.reset()

    def reset(self):
        # Poner modo1 en reset
        self.write8(_MODE1, 0x00)
        time.sleep_ms(10)

    def write8(self, reg, value):
        self.i2c.writeto_mem(self.address, reg, bytes([value]))

    def read8(self, reg):
        return self.i2c.readfrom_mem(self.address, reg, 1)[0]

    def set_freq(self, freq):
        """Establece la frecuencia de PWM en Hz (p.ej. 50 Hz para servos)."""
        prescaleval = 25000000.0
        prescaleval /= 4096.0
        prescaleval /= float(freq)
        prescaleval -= 1.0
        prescale = int(prescaleval + 0.5)

        oldmode = self.read8(_MODE1)
        newmode = (oldmode & 0x7F) | 0x10  # sleep
        self.write8(_MODE1, newmode)      # entrar en modo sleep
        self.write8(_PRESCALE, prescale)
        self.write8(_MODE1, oldmode)
        time.sleep_ms(5)
        self.write8(_MODE1, oldmode | 0xa1)  # auto-increment on

    def set_pwm(self, channel, on, off):
        """Configura el canal (0-15) con valores on/off (0-4095)."""
        reg = _LED0_ON_L + 4*channel
        data = bytes([on & 0xFF, on >> 8, off & 0xFF, off >> 8])
        self.i2c.writeto_mem(self.address, reg, data)
