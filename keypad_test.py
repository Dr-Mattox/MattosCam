from machine import Pin
from time import sleep, time

# Pines del teclado (ajusta según tu conexión)
KEYPAD_ROWS = [26, 27, 14, 12]  # GPIOs para las filas
KEYPAD_COLS = [13, 15, 2, 4]    # GPIOs para las columnas

# Mapeo del teclado matricial
KEYS = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

# Configurar pines
rows = [Pin(pin, Pin.OUT) for pin in KEYPAD_ROWS]
cols = [Pin(pin, Pin.IN, Pin.PULL_DOWN) for pin in KEYPAD_COLS]

# Variables de debounce
last_key_time = 0
debounce_time = 0.3  # Tiempo mínimo entre lecturas de teclas (en segundos)

def read_keypad():
    """Lee una tecla presionada en el teclado matricial con debounce."""
    global last_key_time
    current_time = time()

    # Ignora entradas si no ha pasado suficiente tiempo
    if current_time - last_key_time < debounce_time:
        return None

    for row_idx, row_pin in enumerate(rows):
        row_pin.on()  # Activa la fila
        for col_idx, col_pin in enumerate(cols):
            if col_pin.value():  # Si hay una tecla presionada
                row_pin.off()
                last_key_time = current_time
                return KEYS[row_idx][col_idx]
        row_pin.off()
    return None

# Ejemplo de uso
while True:
    key = read_keypad()
    if key:
        print(f"Tecla presionada: {key}")
    sleep(0.05)
