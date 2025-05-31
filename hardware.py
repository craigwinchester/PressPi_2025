# hardware.py

import RPi.GPIO as GPIO
from config import PIN_SPIN_LEFT, PIN_SPIN_RIGHT, PIN_INFLATE, PIN_DEFLATE
from gpiozero import Button
from drum_position_editor import positions  # for cam_hold_time 

# Track bump count globally (or refactor into a state object)
rotation_count = 0

# --- Bump Button Setup ---
bump_button = None  # declared at module level

# Rotation counter (was `count`)
rotation_count = 0

# --- Bump Button Setup ---
bump_button = None  # module-level reference

def setup_bump_button():
    global bump_button, rotation_count

    cam_hold_time = positions.get("cam_hold_time", 1.0)

    bump_button = Button(21, hold_time=cam_hold_time, pull_up=False)

    def on_bump_start():
        print(f"🔁 Drum bump START — Rotation #{rotation_count}")

    def on_bump_end():
        global rotation_count
        rotation_count += 1
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