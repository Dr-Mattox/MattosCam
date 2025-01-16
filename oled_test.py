# oled_test.py

from machine import Pin, I2C
import time
import ssd1306  # Este es el driver que subiste

# Ajusta segun tu display y pines
i2c = I2C(0, scl=Pin(22), sda=Pin(21))  
# Para ESP32, a veces necesitas: I2C(1, ...) 
# o I2C(freq=400000, scl=Pin(22), sda=Pin(21)) 
# Pero normalmente I2C(0, scl=Pin(22), sda=Pin(21)) esta bien

oled_width = 128
oled_height = 64

oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)  

def test_oled():
    oled.fill(0)  # Limpia la pantalla (0 = negro)
    oled.text("MattosBot", 0, 0)
    oled.text("Hello World!", 0, 10)
    oled.text("1234567890", 0, 20)
    oled.show()
    time.sleep(5)

    # Desplazar el texto o dibujar algo
    oled.fill(0)
    oled.text("Demo scrolldown", 0, 0)
    oled.show()
    for y in range(10, 50, 2):
        oled.scroll(0, -2)
        time.sleep(.2)
        oled.show()

    oled.fill(0)
    oled.text("End of test", 0, 0)
    oled.show()
    time.sleep(2)

test_oled()
