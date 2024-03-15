import serial
import time

interval_seconds = 1

arduino = None
print('serial connected')

def setup_serial_connection():
    global arduino
    arduino = serial.Serial("COM3", 2000000, timeout=0.1)

def motor(fruit, prob):
    if arduino is None:
        raise ValueError("Serial connection not initialized. Call setup_serial_connection() first.")
    
    if fruit == "rottenfruits" and prob > 0.7:
        integer_value = 0
        arduino.write(integer_value.to_bytes(2, 'little'))
        time.sleep(interval_seconds)
    else:
        integer_value = 1
        arduino.write(integer_value.to_bytes(2, 'little'))


setup_serial_connection()
