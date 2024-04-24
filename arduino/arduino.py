def servo(arduino):
    code = 1
    arduino.write(code.to_bytes(2, 'little'))