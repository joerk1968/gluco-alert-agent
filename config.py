# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# 🔑 API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 📞 Twilio Credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# 📱 SMS Settings
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")      # e.g., +12137621916
PATIENT_PHONE_NUMBER = os.getenv("PATIENT_PHONE_NUMBER")    # e.g., +9613929206

# 💬 WhatsApp Settings (more reliable for Lebanon)
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")   # e.g., whatsapp:+14155238886
PATIENT_PHONE_WHATSAPP = os.getenv("PATIENT_PHONE_WHATSAPP")  # e.g., whatsapp:+9613929206

# 🩺 Glucose Thresholds (mg/dL)
HYPO_THRESHOLD = 70   # Alert if ≤ 70
HYPER_THRESHOLD = 180 # Alert if ≥ 180

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
    "TWILIO_WHATSAPP_FROM": TWILIO_WHATSAPP_FROM,
    "PATIENT_PHONE_WHATSAPP": PATIENT_PHONE_WHATSAPP,
}

missing = [key for key, value in required_keys.items() if not value or not value.strip()]
if missing:
    raise ValueError(f"❌ Missing required keys in .env: {missing}")

print("✅ Config loaded: SMS & WhatsApp ready.")