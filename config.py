# config.py - WITH SMS-ONLY MODE FLAG
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# 🔑 API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# 📱 SMS Settings
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")      # e.g., +12137621916
PATIENT_PHONE_NUMBER = os.getenv("PATIENT_PHONE_NUMBER")    # e.g., +9613929206

# 💬 WhatsApp Settings
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")   # e.g., whatsapp:+14155238886
PATIENT_PHONE_WHATSAPP = os.getenv("PATIENT_PHONE_WHATSAPP")  # e.g., whatsapp:+9613929206

# 🚨 TEMPORARY FLAG: Set to True when WhatsApp daily limit is reached
# Set to False after limit resets (midnight UTC)
USE_SMS_ONLY = True  # ⚠️ SET THIS TO TRUE DURING WHATSAPP LIMIT PERIOD

# 🩺 Glucose Thresholds (mg/dL) - MEDICALLY ACCURATE
HYPO_THRESHOLD = 70   # Alert if < 70 (not <= 70)
HYPER_THRESHOLD = 180 # Alert if > 180 (not >= 180)
# config.py - CRITICAL UPDATES
USE_SMS_ONLY = True  # Must be True during WhatsApp daily limit period
HYPO_THRESHOLD = 70   # Alert if < 70 (not <= 70)
HYPER_THRESHOLD = 180 # Alert if > 180 (not >= 180)
# 🧠 LLM Settings
LLM_MODEL = "gpt-4o-mini"
MAX_TOKENS = 300

# ✅ Validate required keys
required_keys = {
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "TWILIO_ACCOUNT_SID": TWILIO_ACCOUNT_SID,
    "TWILIO_AUTH_TOKEN": TWILIO_AUTH_TOKEN,
    "TWILIO_PHONE_NUMBER": TWILIO_PHONE_NUMBER,
    "PATIENT_PHONE_NUMBER": PATIENT_PHONE_NUMBER,
}

missing = [key for key, value in required_keys.items() if not value or not value.strip()]
if missing:
    raise ValueError(f"❌ Missing required keys in .env: {missing}")

print(f"✅ Config loaded: {'SMS-ONLY MODE' if USE_SMS_ONLY else 'WhatsApp + SMS fallback'}")
