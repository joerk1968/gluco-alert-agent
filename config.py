# config.py - CRITICAL SETTINGS
import os
from dotenv import load_dotenv

load_dotenv()

# 🔑 API Keys (from Render environment variables)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# 📱 SMS Settings (MUST be correct for SMS fallback)
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")      # Your Twilio number
PATIENT_PHONE_NUMBER = os.getenv("PATIENT_PHONE_NUMBER")    # Your phone number

# 💬 WhatsApp Settings
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
PATIENT_PHONE_WHATSAPP = os.getenv("PATIENT_PHONE_WHATSAPP")

# 🚨 CRITICAL FLAGS
USE_SMS_ONLY = True  # MUST be True during WhatsApp daily limit period

# 🩺 MEDICALLY ACCURATE THRESHOLDS
HYPO_THRESHOLD = 70   # Alert if < 70 mg/dL (not <= 70)
HYPER_THRESHOLD = 180 # Alert if > 180 mg/dL (not >= 180)

# ✅ Validation
required_keys = [
    "OPENAI_API_KEY", "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN",
    "TWILIO_PHONE_NUMBER", "PATIENT_PHONE_NUMBER"
]

missing = [key for key in required_keys if not os.getenv(key)]
if missing:
    raise ValueError(f"❌ Missing required keys: {missing}")

print(f"✅ Config loaded: SMS-ONLY MODE = {USE_SMS_ONLY}")
