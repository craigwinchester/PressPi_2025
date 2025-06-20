# config.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# GPIO Pin Assignments
PIN_SPIN_LEFT = 17
PIN_SPIN_RIGHT = 27
PIN_INFLATE = [16, 26]
PIN_DEFLATE = [23, 24, 25]
PIN_EXTRA = 22  #save this for future use. 
PIN_BUTTON = 21

# File paths for json 
PROGRAMS_FILE_PATH = BASE_DIR / "json_data" / "programs.json"
POSITIONS_FILE_PATH = BASE_DIR / "json_data" / "drum_position.json"

# Serial Configuration to Arduino & Pressure Transducer
SERIAL_PORT = "/dev/ttyUSB0"
SERIAL_BAUDRATE = 9600  # or 115200 for backup_115200.hx

# Pressure Settings
FULL_DEFLATE = 0.001 #set to 0.001 when ready! 0.6 is good for testing
MAX_PRESSURE = 1.8
FAILSAFE_PRESSURE = 1.9

# Spin Direction for spin_to_location & break-up rotations.
# Left or Right?
SPIN_ROTATION = PIN_SPIN_LEFT

#WEB PAGE On or Off
WEB_SERVER = False

#TouchScreen Attached?
TOUCHSCREEN_ENABLED = True

#Messaging System - text/email/Telegram? see sms_contacts.json & email_contacts.json to add recipients. ATT stopping this service in future.
SMS_MESSAGING = False
CONTACTS_FILE_PATH = BASE_DIR / "json_data" / "sms_contacts.json" 

TELEGRAM_MESSAGING = False
TELEGRAM_BOT_TOKEN = "11111"
TELEGRAM_CHAT_ID = 11111

EMAIL_MESSAGING = False
SMTP_SERVER = "mail.yourServer.com"
SMTP_PORT = 465
SMTP_LOGIN = ""
SMTP_PSWD = ""
EMAIL_FROM = ""
EMAIL_CONTACTS_PATH = BASE_DIR / "json_data" / "email_contacts.json"