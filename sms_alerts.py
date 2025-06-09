#sms_alerts.py
#SMS Alerts & Telegram Message Bot Alerts

import smtplib
import json
from email.mime.text import MIMEText
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, CONTACTS_FILE_PATH, EMAIL_CONTACTS_PATH, SMTP_LOGIN, SMTP_PORT, SMTP_PSWD, SMTP_SERVER, EMAIL_FROM

CARRIER_GATEWAYS = {
    "att": "txt.att.net",
    "verizon": "vtext.com",
    "tmobile": "tmomail.net",
    "sprint": "messaging.sprintpcs.com"
}

def load_email_contacts():
    try:
        with open(EMAIL_CONTACTS_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Failed to load email contacts: {e}")
        return []

def get_email_contact_by_name(name):
    contacts = load_email_contacts()
    for contact in contacts:
        if contact["name"].lower() == name.lower():
            return contact
    print(f"⚠️ No contact found with name '{name}'")
    return None

def load_contacts(file_path=CONTACTS_FILE_PATH):
    try:
        with open(file_path, "r") as f:
            print("SMS contacts loaded")
            return json.load(f)            
    except Exception as e:
        print(f"❌ Error loading contacts: {e}")
        return []
    
def get_contact_by_name(name, file_path=CONTACTS_FILE_PATH):
    try:
        with open(file_path, "r") as f:
            contacts = json.load(f)
        for contact in contacts:
            if contact["name"].lower() == name.lower():
                return contact
        print(f"❌ No contact found with name: {name}")
        return None
    except Exception as e:
        print(f"❌ Error loading contact: {e}")
        return None

def send_sms(contact, message):
    number = contact["number"]
    carrier = contact["carrier"]

    if carrier not in CARRIER_GATEWAYS:
        print(f"❌ Unsupported carrier: {carrier}")
        return

    to_addr = f"{number}@{CARRIER_GATEWAYS[carrier]}"
    msg = MIMEText(message)
    msg["From"] = "craig@lofi-wines.com"
    msg["To"] = to_addr
    msg["Subject"] = "Wine Press Alert"

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_LOGIN, SMTP_PSWD)
            server.sendmail(EMAIL_FROM, [to_addr], msg.as_string())
        print(f"✅ Text sent to {contact['name']}")
    except Exception as e:
        print(f"❌ Failed to send text to {contact['name']}: {e}")

def send_email_message(contact, message):
    to_addr = contact["email"]

    msg = MIMEText(message)
    msg["From"] = "craig@lofi-wines.com"
    msg["To"] = to_addr
    msg["Subject"] = "Wine Press Alert"

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_LOGIN, SMTP_PSWD)
            server.sendmail(EMAIL_FROM, [to_addr], msg.as_string())
        print(f"✅ EMAIL sent to {contact['name']}")
    except Exception as e:
        print(f"❌ Failed to send EMAIL to {contact['name']}: {e}")

def send_telegram_message(message):
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("✅ Telegram message sent.")
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")