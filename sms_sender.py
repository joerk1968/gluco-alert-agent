## sms_sender.py - SMS fallback with Lebanon optimization
from twilio.rest import Client
import os
import time
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_SMS_FROM

def send_sms_alert(glucose_level, timestamp, advice=""):
    """
    Send SMS alert as fallback when WhatsApp fails.
    Optimized for Lebanon carrier deliverability.
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Lebanon-friendly SMS format (avoid medical terms, symbols, long messages)
        status = "LOW" if glucose_level < 70 else "HIGH" if glucose_level > 180 else "OK"
        time_str = timestamp.split('T')[1][:5] if 'T' in timestamp else timestamp
        
        # Simple, carrier-safe message format for Lebanon (+961)
        message_body = f"GLUCO:{time_str}:{status}:{glucose_level}"
        
        # Add simple advice if available (avoid medical terms)
        if advice.strip() and glucose_level < 70:
            message_body += ":EAT_CANDY"
        elif advice.strip() and glucose_level > 180:
            message_body += ":DRINK_WATER"
        
        # Keep under 160 characters for single SMS segment
        message_body = message_body[:140]
        
        print(f"📤 SENDING SMS TO {TWILIO_SMS_FROM} → {os.getenv('PATIENT_SMS')}")
        print(f"💬 SMS Message: {message_body}")
        
        # Send SMS
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_SMS_FROM,
            to=os.getenv("PATIENT_SMS")
        )
        
        print(f"✅ SMS SENT SUCCESSFULLY (SID: {message.sid[:8]})")
        return {
            "success": True,
            "channel": "sms",
            "sid": message.sid,
            "status": message.status
        }
    
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        
        print(f"❌ SMS FAILED: {error_type} - {error_msg}")
        return {
            "success": False,
            "channel": "sms",
            "error": error_type,
            "message": error_msg[:100]
        }
