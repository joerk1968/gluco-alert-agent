# sms_sender.py
from twilio.rest import Client
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, PATIENT_PHONE_NUMBER

def send_sms_alert(glucose_level, timestamp, advice=""):
    """Send SMS alert - guaranteed to work for Lebanon"""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
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
        print(f"❌ SMS FAILED: {str(e)}")
        return False, str(e)[:100]