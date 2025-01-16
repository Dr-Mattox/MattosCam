import time
import math
from machine import Pin, ADC, I2C
import network
import ntptime
import pca9685
import ssd1306

# ------------------ CONFIGURACIONES ------------------

# Wi-Fi
WIFI_SSID = "IZZI-C7C3"
WIFI_PASS = "MISTIMIMOR1818"

# Offset horario (en horas)
TIME_OFFSET_HOURS = -5  

# I2C pines
I2C_SCL = 22
I2C_SDA = 21

# PCA9685
PCA_ADDR = 0x40
SERVO_FREQ = 50

# Servos: tilt=canal 0, pan=canal 1
TILT_CH = 0
PAN_CH = 1

# Modos
MODE_CHILL = "Chill"
MODE_BUSQUEDA = "Busqueda"
MODE_SEGUIMIENTO = "Seguimiento"

current_mode = MODE_BUSQUEDA
current_code = ""  # Código ingresado actualmente (máximo 4 dígitos)

# Estado de movimiento
movement_state = {
    "step": 0,
    "direction": 1,
    "pattern": "none"
}

# Teclado matricial
KEYPAD_ROWS = [26, 27, 14, 12]  # GPIOs para las filas
KEYPAD_COLS = [13, 15, 2, 4]    # GPIOs para las columnas
KEYS = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]
rows = [Pin(pin, Pin.OUT) for pin in KEYPAD_ROWS]
cols = [Pin(pin, Pin.IN, Pin.PULL_DOWN) for pin in KEYPAD_COLS]
last_key_time = 0
debounce_time = 0.3  # Tiempo mínimo entre lecturas de teclas (en segundos)

# ------------------ FUNCIONES ------------------

def angle_to_pwm(angle):
    min_duty = 130
    max_duty = 510
    duty = int(min_duty + (angle / 180.0) * (max_duty - min_duty))
    return duty

def connect_wifi(ssid, password):
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    if not sta.isconnected():
        print(f"Conectando a {ssid}...")
        sta.connect(ssid, password)
        while not sta.isconnected():
            time.sleep(0.5)
    print("WiFi conectado. IP:", sta.ifconfig())

def sync_time_with_ntp(offset_hours=0):
    print("Sincronizando hora con NTP...")
    ntptime.settime()
    print("Hora NTP sincronizada (UTC).")

i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
pca = pca9685.PCA9685(i2c, address=PCA_ADDR)
pca.set_freq(SERVO_FREQ)

def set_servo(channel, angle):
    pwm_val = angle_to_pwm(angle)
    pca.set_pwm(channel, 0, pwm_val)

def get_date_str():
    y, m, d, _, _, _, _, _ = time.localtime(time.time() + TIME_OFFSET_HOURS * 3600)
    return f"{d:02d}/{m:02d}/{y:04d}"

def get_time_str():
    _, _, _, hh, mm, _, _, _ = time.localtime(time.time() + TIME_OFFSET_HOURS * 3600)
    suffix = "AM" if hh < 12 else "PM"
    hh12 = hh % 12 if hh % 12 != 0 else 12
    return f"{hh12:02d}:{mm:02d} {suffix}"

def update_oled_with_code(code):
    oled.fill(0)
    oled.text(get_date_str(), 20, 0)
    oled.text("MattosCam", 0, 15)
    oled.text(f"Modo: {current_mode}", 0, 27)
    oled.text(f"Codigo: {code}", 0, 39)
    oled.text(get_time_str(), 25, 55)
    oled.show()

def read_keypad():
    global last_key_time
    current_time = time.time()
    if current_time - last_key_time < debounce_time:
        return None
    for row_idx, row_pin in enumerate(rows):
        row_pin.on()
        for col_idx, col_pin in enumerate(cols):
            if col_pin.value():
                row_pin.off()
                last_key_time = current_time
                return KEYS[row_idx][col_idx]
        row_pin.off()
    return None

def process_key(key):
    global current_code, current_mode
    if key.isdigit() and len(current_code) < 4:
        current_code += key
    elif key == '*':
        current_code = current_code[:-1]
    elif key == '#':
        print(f"Codigo confirmado: {current_code}")
        current_code = ""
    elif key == 'A':
        current_mode = MODE_CHILL
        movement_state.update({"pattern": "chill", "step": 0, "direction": 1})
    elif key == 'B':
        current_mode = MODE_BUSQUEDA
        movement_state.update({"pattern": "busqueda", "step": 0, "direction": 1})
    elif key == 'C':
        current_mode = MODE_SEGUIMIENTO
        movement_state.update({"pattern": "seguimiento", "step": 0, "direction": 1})
    elif key == 'D':
        print("Laser encendido/apagado")
    update_oled_with_code(current_code)

def move_pattern():
    step = movement_state["step"]
    direction = movement_state["direction"]
    if movement_state["pattern"] == "chill":
        tilt_ang = 90 + int(math.sin(step * math.pi / 30) * 10)
        set_servo(PAN_CH, 60 + step)
        set_servo(TILT_CH, tilt_ang)
        movement_state["step"] += direction
        if step >= 60 or step <= 0:
            movement_state["direction"] *= -1
    elif movement_state["pattern"] == "busqueda":
        pan_ang = step % 180
        tilt_ang = 60 if (step // 180) % 2 == 0 else 120
        set_servo(PAN_CH, pan_ang)
        set_servo(TILT_CH, tilt_ang)
        movement_state["step"] += 5
    elif movement_state["pattern"] == "seguimiento":
        pan_ang = 90 + int(math.sin(step * 0.1) * 30)
        tilt_ang = 90 + int(math.cos(step * 0.1) * 20)
        set_servo(PAN_CH, pan_ang)
        set_servo(TILT_CH, tilt_ang)
        movement_state["step"] += 5

def main():
    global current_mode
    connect_wifi(WIFI_SSID, WIFI_PASS)
    sync_time_with_ntp()
    current_mode = MODE_BUSQUEDA
    update_oled_with_code(current_code)
    while True:
        key = read_keypad()
        if key:
            process_key(key)
        move_pattern()
        time.sleep(0.05)

if __name__ == "__main__":
    main()
