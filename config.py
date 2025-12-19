# config.py - DEBUG VERSION
import os

# Get these from environment - NO DEFAULTS
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "")
PATIENT_PHONE_NUMBER = os.environ.get("PATIENT_PHONE_NUMBER", "")

# Debug print
print("🔐 TWILIO CREDENTIALS LOADED:")
print(f"   SID: {'SET' if TWILIO_ACCOUNT_SID else 'NOT SET'}")
print(f"   TOKEN: {'SET' if TWILIO_AUTH_TOKEN else 'NOT SET'}")
print(f"   FROM: {TWILIO_PHONE_NUMBER}")
print(f"   TO: {PATIENT_PHONE_NUMBER}")

# Medical thresholds
LOW_GLUCOSE = 70
HIGH_GLUCOSE = 180