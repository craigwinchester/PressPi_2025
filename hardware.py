# hardware.py

import RPi.GPIO as GPIO
import serial
import time
import json
import status
from config import PIN_SPIN_LEFT, PIN_SPIN_RIGHT, PIN_INFLATE, PIN_DEFLATE, SERIAL_PORT, SERIAL_BAUDRATE, WEB_SERVER
from gpiozero import Button
from drum_position_editor import positions  # for cam_hold_time 
from web_server import update_pressure_history

ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=2)
ser.baudrate = SERIAL_BAUDRATE

# Track bump count globally (or refactor into a state object)
rotationCount = 0

# --- Bump Button Setup ---
bump_button = None  # declared at module level

def setup_bump_button():
    global bump_button, rotationCount

    cam_hold_time = positions.get("cam_hold_time", 1.0)

    bump_button = Button(21, hold_time=cam_hold_time, pull_up=False)

    def on_bump_start():
        print(f"🔁 Drum bump START — Rotation #{rotationCount}")

    def on_bump_end():
        global rotationCount
        rotationCount += 1
        print("🛑 Drum bump END")

    def on_bump_held():
        print("⏳ Cam held the button — long bump detected")

    bump_button.when_pressed = on_bump_start
    bump_button.when_released = on_bump_end
    bump_button.when_held = on_bump_held

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    # Combine all pins to one list
    all_pins = [PIN_SPIN_LEFT, PIN_SPIN_RIGHT] + PIN_INFLATE + PIN_DEFLATE

    # Initialize each as output and set HIGH to keep relays off (or LOW depending on relay type)
    for pin in all_pins:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)
    
    print("[HARDWARE] GPIO initialized")

    setup_bump_button()
    print("[HARDWARE] bump button initialized")

def cleanup_gpio():
    GPIO.cleanup()
    print("[HARDWARE] GPIO cleanup complete")

def getCurrentBar():
    try:
        line = ser.readline()
        decoded = line.decode('utf-8', errors='ignore').strip()
        return float(decoded)
    except Exception as e:
        print(f"[getCurrentBar error] {e}")
        return 0.0

def pressure_updater():
    while True:
        status.pressure_data = getCurrentBar()
        if WEB_SERVER:
            try:
                update_pressure_history(status.pressure_data)
                with open("/tmp/pressure_log.json","w") as f:
                    json.dump({"pressure": status.pressure_data,
                            "program": status.current_program_data,
                            "totalStage": status.total_stage_data,
                            "stage": status.current_stage_data,
                            "totalCycle": status.total_cycle_data,
                            "cycle": status.current_cycle_data,
                            "action": status.current_action
                    }, f)
            except Exception as e: 
                print(f"Error writing pressure: {e}")
        time.sleep(0.1)

def update_json_pressure_log(pressure):  #keeps all other data intact and only updates pressure.
    try:
        with open("/tmp/pressure_log.json", "r") as f:
            data = json.load(f)
    except:
        data = {}

    data["pressure"] = pressure

    with open("/tmp/pressure_log.json", "w") as f:
        json.dump(data, f)