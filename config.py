# config.py

# GPIO Pin Assignments
PIN_SPIN_LEFT = 17
PIN_SPIN_RIGHT = 27
PIN_INFLATE = [16, 26]
PIN_DEFLATE = [23, 24, 25]

# File paths for json 
PROGRAMS_FILE_PATH = "/home/craig/Documents/CODE/Raspberry_Pi_Wine_Press/programs.json"
POSITIONS_FILE_PATH = "/home/craig/Documents/CODE/Raspberry_Pi_Wine_Press/drum_position.json"

# Serial Configuration to Arduino & Pressure Transducer
SERIAL_PORT = "/dev/ttyUSB0"
SERIAL_BAUDRATE = 115200

# Pressure Settings
FULL_DEFLATE = 0.001 #set to 0.001 when ready! 0.6 is good for testing
MAX_PRESSURE = 1.8

# Spin Direction for spin_to_location & break-up rotations.
# Left or Right?
SPIN_ROTATION = PIN_SPIN_LEFT

#WEB PAGE On or Off
WEB_SERVER = False