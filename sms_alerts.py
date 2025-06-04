#sms_alerts.py

import smtplib
import json
from email.mime.text import MIMEText

CARRIER_GATEWAYS = {
    "att": "txt.att.net",
    "verizon": "vtext.com",
    "tmobile": "tmomail.net",
    "sprint": "messaging.sprintpcs.com"
}

def load_contacts(file_path="sms_contacts.json"):
    try:
        with open(file_path, "r") as f:
            print("SMS contacts loaded")
            return json.load(f)            
    except Exception as e:
        print(f"❌ Error loading contacts: {e}")
        return []
    
def get_contact_by_name(name, file_path="sms_contacts.json"):
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
        with smtplib.SMTP_SSL("mail.lofi-wines.com", 465) as server:
            server.login("craig@lofi-wines.com", "Chang3*m3")
            server.sendmail(msg["From"], [to_addr], msg.as_string())
        print(f"✅ Text sent to {contact['name']}")
    except Exception as e:
        print(f"❌ Failed to send text to {contact['name']}: {e}")