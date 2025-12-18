# config.py - CLEAN VERSION WITHOUT MERGE MARKERS
import os
from dotenv import load_dotenv

load_dotenv()

# 🔑 API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "dummy_key_for_local_testing")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "dummy_sid_for_local_testing")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "dummy_token_for_local_testing")

# 📱 SMS Settings
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+12137621916")
PATIENT_PHONE_NUMBER = os.getenv("PATIENT_PHONE_NUMBER", "+9613929206")

# 💬 WhatsApp Settings
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
PATIENT_PHONE_WHATSAPP = os.getenv("PATIENT_PHONE_WHATSAPP", "whatsapp:+9613929206")

# 🚨 Critical flags
USE_SMS_ONLY = True  # Set to True during WhatsApp daily limit period

# 🩺 Medical thresholds
HYPO_THRESHOLD = 70   # Alert if < 70 mg/dL
HYPER_THRESHOLD = 180 # Alert if > 180 mg/dL

# 🧠 LLM Settings
LLM_MODEL = "gpt-4o-mini"
MAX_TOKENS = 300

print("✅ Config loaded successfully")
print(f"🧠 LLM Model: {LLM_MODEL}")
print(f"🩺 Thresholds: Hypo < {HYPO_THRESHOLD}, Hyper > {HYPER_THRESHOLD}")
print(f"📱 WhatsApp mode: {'DISABLED (SMS only)' if USE_SMS_ONLY else 'ENABLED'}")