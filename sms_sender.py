# sms_sender.py
from twilio.rest import Client
import os

def send_glucose_alert(glucose_level, timestamp, advice=""):
    """Send SMS alert with glucose information"""
    try:
        # Get credentials from environment
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_PHONE_NUMBER")
        to_number = os.getenv("PATIENT_PHONE_NUMBER")
        
        if not all([account_sid, auth_token, from_number, to_number]):
            return "❌ MISSING TWILIO CREDENTIALS - check Render environment variables"
        
        client = Client(account_sid, auth_token)
        
        # Build simple SMS message
        status = "LOW" if glucose_level < 70 else "HIGH" if glucose_level > 180 else "OK"
        time_str = timestamp.split('T')[1][:5]
        message_body = f"GLUCO TEST:{time_str}|{glucose_level}mg/dL|{status}|{advice[:50]}"
        
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number
        )
        return f"✅ SMS SENT (SID: {message.sid[:8]})"
    
    except Exception as e:
        return f"❌ SMS FAILED: {str(e)}"
