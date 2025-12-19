# sms_sender.py - DEBUG VERSION
from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, PATIENT_PHONE_NUMBER
import os

def send_sms_alert(glucose_level, timestamp, advice=""):
    """Send SMS alert with detailed debugging"""
    try:
        print("🔍 DEBUGGING TWILIO CREDENTIALS:")
        print(f"   Account SID from config: {TWILIO_ACCOUNT_SID[:8]}...{TWILIO_ACCOUNT_SID[-4:]}")
        print(f"   Auth Token from config: {TWILIO_AUTH_TOKEN[:4]}...{TWILIO_AUTH_TOKEN[-4:]}")
        print(f"   From number: {TWILIO_PHONE_NUMBER}")
        print(f"   To number: {PATIENT_PHONE_NUMBER}")
        
        # Try to create client
        print("🔧 CREATING TWILIO CLIENT...")
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        print("✅ TWILIO CLIENT CREATED SUCCESSFULLY")
        
        # Lebanon-friendly message format
        time_str = timestamp.split('T')[1][:5]
        status = "LOW" if glucose_level < 70 else "HIGH" if glucose_level > 180 else "OK"
        
        message_body = f"GLUCO TEST:{time_str}|{status}:{glucose_level}mg/dL:{advice[:30]}"
        message_body = message_body[:140]  # Keep under 160 chars
        
        print(f"📤 SENDING SMS TO {PATIENT_PHONE_NUMBER}: {message_body}")
        
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=PATIENT_PHONE_NUMBER
        )
        
        print(f"✅ SMS SENT SUCCESSFULLY (SID: {message.sid[:8]})")
        return True, message.sid[:8]
    
    except Exception as e:
        error_type = type(e).__name__
        print(f"❌ SMS FAILED: {error_type} - {str(e)}")
        print("🔧 ENVIRONMENT VARIABLES IN RENDER:")
        for key in ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_PHONE_NUMBER", "PATIENT_PHONE_NUMBER"]:
            value = os.environ.get(key)
            print(f"   {key}: {'FOUND' if value else 'MISSING'}")
        return False, f"{error_type}: {str(e)[:100]}"