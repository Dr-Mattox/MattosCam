# two_servos_test.py

from machine import Pin, I2C
import time
import pca9685

def angle_to_pwm(angle):
    """
    Ajusta estos valores (min_duty y max_duty) 
    para que tu servo no fuerce al llegar a 0° o 180°.
    """
    min_duty = 130   # Pulso ~0.65ms (aprox 0°)
    max_duty = 510   # Pulso ~2.45ms (aprox 180°)
    duty = int(min_duty + (angle/180.0)*(max_duty - min_duty))
    return duty

# Inicializa I2C y PCA9685
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
pca = pca9685.PCA9685(i2c, address=0x40)
pca.set_freq(50)  # 50Hz: frecuencia típica para servos

# Definimos en qué canales están los dos servos
SERVO_PAN_CHANNEL = 0
SERVO_TILT_CHANNEL = 1

def move_servos(pan_angle, tilt_angle):
    """
    Mueve el servo de pan y tilt a los ángulos especificados.
    """
    pan_pwm = angle_to_pwm(pan_angle)
    tilt_pwm = angle_to_pwm(tilt_angle)
    pca.set_pwm(SERVO_PAN_CHANNEL, 0, pan_pwm)
    pca.set_pwm(SERVO_TILT_CHANNEL, 0, tilt_pwm)

print("Iniciando test de 2 servos en rangos completos...")

# Ejemplo 1: ambos servos recorren 0° -> 180° al mismo tiempo
for ang in range(0, 181, 5):
    move_servos(ang, ang)
    time.sleep(0.05)

# Pausa de 1s
time.sleep(1)

# Ejemplo 2: ambos servos regresan 180° -> 0° al mismo tiempo
for ang in range(180, -1, -5):
    move_servos(ang, ang)
    time.sleep(0.05)

time.sleep(1)

# Ejemplo 3: servo de pan va de 0°->180° mientras tilt va de 180°->0°
for ang in range(0, 181, 5):
    move_servos(ang, 180 - ang)
    time.sleep(0.05)

time.sleep(1)

# Ejemplo 4: un mini "barrido alterno" (tilt fijo, pan se mueve, luego al reves)
# Pan: 0->180->0, Tilt se mantiene en 90
move_servos(0, 90)
for ang in range(0, 181, 5):
    move_servos(ang, 90)
    time.sleep(0.05)
for ang in range(180, -1, -5):
    move_servos(ang, 90)
    time.sleep(0.05)

# Tilt: 0->180->0, mientras Pan se queda en 90
move_servos(90, 0)
for ang in range(0, 181, 5):
    move_servos(90, ang)
    time.sleep(0.05)
for ang in range(180, -1, -5):
    move_servos(90, ang)
    time.sleep(0.05)

print("Test finalizado. Servos en posicion (90, 90).")
# Dejamos servos en posicion central
move_servos(90, 90)
