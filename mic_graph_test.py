from machine import Pin, ADC
import time

# Ajusta según el pin ADC que hayas elegido:
MIC_PIN = 34

# Configuración del ADC
mic_adc = ADC(Pin(MIC_PIN))
mic_adc.atten(ADC.ATTN_11DB)  # hasta ~3.3-3.6V máximo

def draw_bar(value, max_adc=4095, bar_width=60):
    """
    Dibuja una barra (#) en la consola según 'value'.
    - value: lectura del ADC (0 a 4095).
    - max_adc: valor máximo esperado (4095 en ESP32).
    - bar_width: longitud máxima de la barra en caracteres.
    """
    # Escalamos 'value' al rango [0..bar_width]
    proportion = value / max_adc
    bar_len = int(proportion * bar_width)
    
    # Creamos la barra con '#' y rellenamos con espacios
    bar_str = '#' * bar_len
    # Generamos un string para mostrar
    return f"{value:4d} |{bar_str}"

def mic_test():
    print("=== Iniciando grafica de microfono (presiona Ctrl+C para salir) ===\n")
    time.sleep(2)
    
    while True:
        val = mic_adc.read()       # Lectura del ADC (0..4095)
        bar_line = draw_bar(val)   # Genera la linea con barras
        print(bar_line)            # Imprime en la consola REPL
        time.sleep(0.05)           # Ajusta la velocidad de refresco

# Si prefieres que se ejecute directo al importar:
if __name__ == "__main__":
    mic_test()
