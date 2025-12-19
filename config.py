# config.py
import os

# Get these from your Render Environment tab later
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "AC636f695a472e0c37cb2a02cafbb7579d")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "1fbafadebe35dd911f8d48ab51f8a7f7")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "+12137621916")
PATIENT_PHONE_NUMBER = os.getenv("PATIENT_PHONE_NUMBER", "+9613929206")

# Medical thresholds
LOW_GLUCOSE = 70
HIGH_GLUCOSE = 180