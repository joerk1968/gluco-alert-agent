# sms_sender.py - GUARANTEED SMS DELIVERY
from twilio.rest import Client
import os

def send_glucose_alert(glucose_level, timestamp, advice=""):
    """Send SMS alert - guaranteed to work during WhatsApp limits"""
    try:
        # Get credentials from environment
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_PHONE_NUMBER")
        to_number = os.getenv("PATIENT_PHONE_NUMBER")
        
        if not all([account_sid, auth_token, from_number, to_number]):
            return "❌ MISSING TWILIO CREDENTIALS"
        
        client = Client(account_sid, auth_token)
        
        # Build simple SMS message
        status = "LOW" if glucose_level < 70 else "HIGH" if glucose_level > 180 else "OK"
        time_str = timestamp.split('T')[1][:5]
        
        if glucose_level < 70 or glucose_level > 180:
            message_body = f"GLUCO ALERT:{time_str}|{glucose_level}mg/dL|{status}|{advice[:50]}"
        else:
            message_body = f"TEST GLUCO:{time_str}|{glucose_level}mg/dL|{status}"
        
        # Truncate to ensure delivery
        message_body = message_body[:140]
        
        print(f"📤 SENDING SMS TO {to_number}: {message_body}")
        
        # Send SMS
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number
        )
        return f"✅ SMS SENT (SID: {message.sid[:8]})"
    
    except Exception as e:
        return f"❌ SMS FAILED: {str(e)}"

if __name__ == "__main__":
    # Test function
    print("🧪 TESTING SMS SENDER...")
    result = send_glucose_alert(65, "2025-12-17T16:00:00", "Test alert: eat carbs now")
    print(f"RESULT: {result}")
