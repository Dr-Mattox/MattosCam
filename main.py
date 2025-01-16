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

# Micrófono
MIC_PIN = 34
SOUND_THRESHOLD = 500
WINDOW_SECONDS = 2.0

# Modos
MODE_CHILL = "Chill"
MODE_BUSQUEDA = "Busqueda"
MODE_SEGUIMIENTO = "Seguimiento"

current_mode = MODE_BUSQUEDA
current_code = ""  # Código ingresado actualmente (máximo 4 dígitos)

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

mic_adc = ADC(Pin(MIC_PIN))
mic_adc.atten(ADC.ATTN_11DB)

def update_oled_with_code(code):
    oled.fill(0)
    oled.text("MattosCam", 0, 16)
    oled.text(f"Modo: {current_mode}", 0, 32)
    oled.text(f"Codigo: {code}", 0, 48)
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
    elif key == 'B':
        current_mode = MODE_BUSQUEDA
    elif key == 'C':
        current_mode = MODE_SEGUIMIENTO
    elif key == 'D':
        print("Láser encendido/apagado")
    update_oled_with_code(current_code)

def detect_sound_once(threshold=SOUND_THRESHOLD, window=WINDOW_SECONDS):
    start = time.time()
    while (time.time() - start) < window:
        val = mic_adc.read()
        if val > threshold:
            while mic_adc.read() > threshold:
                time.sleep(0.01)
            return True
        time.sleep(0.01)
    return False

def do_chill():
    for pan_ang in range(60, 121, 2):
        tilt_ang = 90 + int(math.sin(pan_ang * math.pi / 30) * 10)
        tilt_ang = max(80, min(100, tilt_ang))
        set_servo(PAN_CH, pan_ang)
        set_servo(TILT_CH, tilt_ang)
        time.sleep(0.05)
    for pan_ang in range(120, 59, -2):
        tilt_ang = 90 + int(math.sin(pan_ang * math.pi / 30) * 10)
        tilt_ang = max(80, min(100, tilt_ang))
        set_servo(PAN_CH, pan_ang)
        set_servo(TILT_CH, tilt_ang)
        time.sleep(0.05)

def do_busqueda():
    set_servo(PAN_CH, 90)
    for t in range(60, 121, 5):
        set_servo(TILT_CH, t)
        time.sleep(0.03)
    set_servo(TILT_CH, 90)
    for p in range(0, 181, 5):
        set_servo(PAN_CH, p)
        time.sleep(0.03)
    for deg in range(0, 360, 5):
        r = math.radians(deg)
        p = 90 + int(math.sin(r) * 30)
        t = 90 + int(math.cos(r) * 30)
        set_servo(PAN_CH, p)
        set_servo(TILT_CH, t)
        time.sleep(0.03)

def do_seguimiento():
    base_pan = 90
    base_tilt = 90
    for i in range(50):
        off_p = int(math.sin(i * 0.2) * 10)
        off_t = int(math.cos(i * 0.2) * 5)
        set_servo(PAN_CH, base_pan + off_p)
        set_servo(TILT_CH, base_tilt + off_t)
        time.sleep(0.05)

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
        if current_mode == MODE_CHILL:
            do_chill()
        elif current_mode == MODE_BUSQUEDA:
            do_busqueda()
        elif current_mode == MODE_SEGUIMIENTO:
            do_seguimiento()

if __name__ == "__main__":
    main()
