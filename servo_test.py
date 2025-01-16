# servo_test.py

from machine import Pin, I2C
import time
import pca9685

def angle_to_pwm(angle):
    # Ajusta segun tu servo
    min_duty = 130   # duty count ~ 0.65ms
    max_duty = 510   # duty count ~ 2.45ms
    duty = int(min_duty + (angle/180.0)*(max_duty - min_duty))
    return duty

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
pca = pca9685.PCA9685(i2c)
pca.set_freq(50)

servo_channel = 0

while True:
    # 0 a 180
    for ang in range(0, 181, 10):
        pwm_val = angle_to_pwm(ang)
        pca.set_pwm(servo_channel, 0, pwm_val)
        time.sleep(0.5)

    # 180 a 0
    for ang in range(180, -1, -10):
        pwm_val = angle_to_pwm(ang)
        pca.set_pwm(servo_channel, 0, pwm_val)
        time.sleep(0.5)
