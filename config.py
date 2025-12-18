# config.py - WhatsApp-first configuration
import os
from dotenv import load_dotenv

load_dotenv()

# 🔑 API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# 📱 WhatsApp Settings (PRIMARY)
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")   # whatsapp:+14155238886
PATIENT_WHATSAPP = os.getenv("PATIENT_WHATSAPP")  # whatsapp:+9613929206

# 📱 SMS Settings (FALLBACK)
TWILIO_SMS_FROM = os.getenv("TWILIO_SMS_FROM")    # +12137621916
PATIENT_SMS = os.getenv("PATIENT_SMS")             # +9613929206

# 🚨 Critical flags
USE_WHATSAPP_FIRST = True  # Try WhatsApp first, then SMS fallback
MAX_RETRY_ATTEMPTS = 2     # Retry failed messages

# 🩺 Medical thresholds
HYPO_THRESHOLD = 70   # Alert if < 70 mg/dL
HYPER_THRESHOLD = 180 # Alert if > 180 mg/dL

# 🧠 LLM Settings
LLM_MODEL = "gpt-4o-mini"
MAX_TOKENS = 300

# ✅ Validation
required_keys = [
    "TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN",
    "TWILIO_WHATSAPP_FROM", "PATIENT_WHATSAPP",
    "TWILIO_SMS_FROM", "PATIENT_SMS"
]

missing = [key for key in required_keys if not os.getenv(key)]
if missing:
    print(f"⚠️ Missing required keys: {missing}")
else:
    print("✅ Config loaded: WhatsApp-first with SMS fallback")
