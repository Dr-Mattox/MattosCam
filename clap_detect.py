# clap_detect.py

from machine import Pin, ADC
import time

mic_adc = ADC(Pin(34))
mic_adc.atten(ADC.ATTN_11DB)

CLAP_THRESHOLD = 1000  # Ajustar según tu módulo
CLAP_WINDOW = 2      # segundos para contar aplausos consecutivos

def detect_claps():
    """
    Retorna la cantidad de aplausos consecutivos detectados (0,1,2,3,...).
    Si no detecta nada en 'CLAP_WINDOW', retorna 0.
    """
    clap_count = 0
    start_time = time.time()
    
    while True:
        val = mic_adc.read()
        
        if val > CLAP_THRESHOLD:
            # Se detecta un pico -> consideramos un aplauso
            clap_count += 1
            # Espera a que baje para no contar múltiples picos del mismo aplauso
            while mic_adc.read() > CLAP_THRESHOLD:
                time.sleep(0.02)
        
        # Si pasamos CLAP_WINDOW segundos, salimos y retornamos
        if (time.time() - start_time) > CLAP_WINDOW:
            return clap_count
        
        time.sleep(0.02)

if __name__ == "__main__":
    while True:
        c = detect_claps()
        if c == 2:
            print("Se detectaron 2 aplausos! (modo buscar persona)")
        elif c == 3:
            print("Se detectaron 3 aplausos! (modo dejar de seguir)")
        elif c > 0:
            print(f"Se detectaron {c} aplausos (otros)")
