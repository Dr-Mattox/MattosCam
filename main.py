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

# Offset horario (en horas). 
# Ej: Si tu RTC marca 8:40 cuando son 3:40, offset = -5
TIME_OFFSET_HOURS = -5  

# I2C pines
I2C_SCL = 22
I2C_SDA = 21

# PCA9685
PCA_ADDR = 0x40
SERVO_FREQ = 50

# Servos: tilt=canal 0, pan=canal 1
TILT_CH = 0
PAN_CH  = 1

# Micrófono
MIC_PIN = 34
SOUND_THRESHOLD = 500
WINDOW_SECONDS  = 2.0

# Modos
MODE_CHILL      = "Chill"
MODE_BUSQUEDA   = "Busqueda"
MODE_SEGUIMIENTO= "Seguimiento"

current_mode    = MODE_BUSQUEDA

# Rango calibración (ajusta a tu servo)
def angle_to_pwm(angle):
    min_duty = 130   # ~0.65ms
    max_duty = 510   # ~2.45ms
    duty = int(min_duty + (angle/180.0)*(max_duty - min_duty))
    return duty

# ------------------ INICIALIZACIÓN ------------------

# 1. Wi-Fi
def connect_wifi(ssid, password):
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    if not sta.isconnected():
        print(f"Conectando a {ssid}...")
        sta.connect(ssid, password)
        while not sta.isconnected():
            time.sleep(0.5)
    print("WiFi conectado. IP:", sta.ifconfig())

# 2. Sincronizar hora con NTP, con offset
def sync_time_with_ntp(offset_hours=0):
    print("Sincronizando hora con NTP...")
    ntptime.settime()  # Ajusta RTC con UTC
    print("Hora NTP sincronizada (UTC).")
    # No ajusta automáticamente la zona. Lo haremos en get_local_time().

# 3. I2C, OLED y PCA9685
i2c = I2C(0, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
pca  = pca9685.PCA9685(i2c, address=PCA_ADDR)
pca.set_freq(SERVO_FREQ)

def set_servo(channel, angle):
    pwm_val = angle_to_pwm(angle)
    pca.set_pwm(channel, 0, pwm_val)

# 4. ADC para micrófono
from machine import ADC
mic_adc = ADC(Pin(MIC_PIN))
mic_adc.atten(ADC.ATTN_11DB)

# ------------------ FUNCIONES DE HORA Y FECHA ------------------

def get_local_time():
    """
    Retorna una tupla localtime con offset aplicado.
    (year, month, mday, hour, minute, second, weekday, yearday)
    """
    # Obtenemos la hora UTC del RTC
    t_utc = time.time()
    # Sumamos offset en segundos
    local_t = t_utc + TIME_OFFSET_HOURS * 3600
    return time.localtime(local_t)

def get_date_str():
    """
    Devuelve la fecha en formato DD/MM/YYYY (ej: 12/01/2024).
    """
    y, m, d, hh, mm, ss, wd, yd = get_local_time()
    return f"{d:02d}/{m:02d}/{y:04d}"

def get_time_str():
    """
    Devuelve la hora con AM/PM. 
    Ej: "03:40 PM"
    """
    y, m, d, hh, mm, ss, wd, yd = get_local_time()
    suffix = "AM"
    if hh >= 12:
        suffix = "PM"
    hh12 = hh % 12
    if hh12 == 0:
        hh12 = 12
    return f"{hh12:02d}:{mm:02d} {suffix}"

# ------------------ OLED ------------------
def update_oled(mode_str):
    # Limpia pantalla
    oled.fill(0)

    # Fecha arriba
    date_s = get_date_str()
    oled.text(date_s, 0, 0)

    # MattosCam + Modo en el medio
    oled.text("MattosCam", 0, 16)
    oled.text(f"Modo: {mode_str}", 0, 32)

    # Hora abajo
    time_s = get_time_str()
    oled.text(time_s, 0, 56)
    oled.show()

# ------------------ DETECCIÓN DE SONIDO ------------------
def detect_sound_once(threshold=SOUND_THRESHOLD, window=WINDOW_SECONDS):
    """
    Lee el ADC durante 'window' segundos.
    Si encuentra un valor > threshold, retorna True.
    """
    start = time.time()
    while (time.time() - start) < window:
        val = mic_adc.read()
        if val > threshold:
            # Esperamos a que baje
            while mic_adc.read() > threshold:
                time.sleep(0.01)
            return True
        time.sleep(0.01)
    return False

# ------------------ MOVIMIENTOS POR MODO ------------------

def do_chill():
    """
    Rango pan: 60..120
    Rango tilt: 80..100
    Movimiento lento con algo de vaivén.
    """
    for pan_ang in range(60, 121, 2):
        # tilt_ang oscila entre 80 y 100 con una sinusoide
        # pivot = 90 (mitad de 80..100)
        # amplitud = 10
        tilt_ang = 90 + int(math.sin(pan_ang * math.pi / 30) * 10)
        # asegurarse de no salir de [80..100]
        if tilt_ang < 80:
            tilt_ang = 80
        if tilt_ang > 100:
            tilt_ang = 100

        set_servo(PAN_CH, pan_ang)
        set_servo(TILT_CH, tilt_ang)
        time.sleep(0.05)

    for pan_ang in range(120, 59, -2):
        tilt_ang = 90 + int(math.sin(pan_ang * math.pi / 30) * 10)
        if tilt_ang < 80:
            tilt_ang = 80
        if tilt_ang > 100:
            tilt_ang = 100

        set_servo(PAN_CH, pan_ang)
        set_servo(TILT_CH, tilt_ang)
        time.sleep(0.05)

def do_busqueda():
    """
    Movimiento con varios patrones,
    simulando que busca algo.
    (Igual que antes, solo ejemplo)
    """
    # Patrón vertical: tilt 60..120, pan fijo en 90
    set_servo(PAN_CH, 90)
    for t in range(60, 121, 5):
        set_servo(TILT_CH, t)
        time.sleep(0.03)

    # Patrón horizontal: pan 0..180, tilt=90
    set_servo(TILT_CH, 90)
    for p in range(0, 181, 5):
        set_servo(PAN_CH, p)
        time.sleep(0.03)

    # Patrón "circular" sin/cos
    for deg in range(0, 360, 5):
        r = math.radians(deg)
        p = 90 + int(math.sin(r)*30)
        t = 90 + int(math.cos(r)*30)
        set_servo(PAN_CH, p)
        set_servo(TILT_CH, t)
        time.sleep(0.03)

def do_seguimiento():
    """
    Modo de seguimiento simulado.
    """
    base_pan = 90
    base_tilt= 90
    for i in range(50):
        # Pequeño vaivén
        off_p = int(math.sin(i*0.2)*10)
        off_t = int(math.cos(i*0.2)*5)
        set_servo(PAN_CH, base_pan + off_p)
        set_servo(TILT_CH, base_tilt + off_t)
        time.sleep(0.05)

# ------------------ MAIN ------------------

def main():
    global current_mode

    # 1. Conectar Wi-Fi, sincronizar NTP
    connect_wifi(WIFI_SSID, WIFI_PASS)
    sync_time_with_ntp()

    # Inicia en modo Chill
    current_mode = MODE_BUSQUEDA
    update_oled(current_mode)

    while True:
        # Si detectamos sonido, forzamos modo Chill
        if detect_sound_once():
            current_mode = MODE_CHILL
            update_oled(current_mode)

        # Ejecutar movimientos del modo actual
        if current_mode == MODE_CHILL:
            do_chill()
        elif current_mode == MODE_BUSQUEDA:
            do_busqueda()
        elif current_mode == MODE_SEGUIMIENTO:
            do_seguimiento()

        # Aquí podrías cambiar a busqueda/seguimiento con algo extra,
        # p. ej. teclado, socket, etc. 
        # Por ahora se queda en Chill hasta que lo modifiques.

if __name__ == "__main__":
    main()
