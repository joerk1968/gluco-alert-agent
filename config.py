# config.py
import os

# Get from environment variables
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
PATIENT_PHONE_NUMBER = os.getenv("PATIENT_PHONE_NUMBER")

if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, PATIENT_PHONE_NUMBER]):
    print("⚠️ WARNING: Missing Twilio credentials - SMS will fail")
