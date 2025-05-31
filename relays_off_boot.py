import RPi.GPIO as GPIO
import time
from datetime import datetime

# List your GPIO pins connected to relays here
relay_pins = [17, 27, 22, 23, 24, 25, 16, 26]  

GPIO.setmode(GPIO.BCM)

# Initialize all relay pins
for pin in relay_pins:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.HIGH)  # HIGH = OFF for active-low relays

time.sleep(0.5)

# Log confirmation
with open("/home/craig/Documents/CODE/Raspberry_Pi_Wine_Press/relay_log.txt", "a") as log:  #change directory as needed
    log.write(f"[{datetime.now()}] Relays set to OFF\n")

GPIO.cleanup()  