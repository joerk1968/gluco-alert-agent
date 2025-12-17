# sms_sender.py - FIXED FOR RELIABLE SMS DELIVERY
from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
    PATIENT_PHONE_NUMBER
)

def send_glucose_alert(glucose_level, timestamp, advice=""):
    """
    Sends an SMS alert with glucose level and advice.
    Designed for maximum deliverability in Lebanon (+961).
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Determine status (short: LOW/HIGH/OK)
        if glucose_level <= 70:
            status = "LOW"
        elif glucose_level >= 180:
            status = "HIGH"
        else:
            status = "OK"
        
        # Build minimal, carrier-friendly message (under 160 chars)
        time_str = timestamp.split('T')[1][:5]  # e.g., "14:30"
        
        if advice and advice.strip():
            # Take only first sentence for SMS
            first_sentence = advice.strip().split('.')[0].split('!')[0].strip()
            message_body = f"GLUCO ALERT:{time_str}|{glucose_level}mg/dL|{status}|{first_sentence}"
        else:
            message_body = f"GLUCO:{time_str}|{glucose_level}mg/dL|{status}"
        
        # Final safety: truncate to 140 chars (1 SMS segment)
        message_body = message_body[:140]
        
        print(f"📤 SENDING SMS TO {PATIENT_PHONE_NUMBER}: {message_body}")
        
        # Send SMS
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=PATIENT_PHONE_NUMBER
        )
        return f"✅ SMS sent (SID: {message.sid[:8]}...)"
    
    except Exception as e:
        error_msg = f"❌ SMS failed: {type(e).__name__}: {str(e)}"
        print(error_msg)
        return error_msg

# 🔬 Test
if __name__ == "__main__":
    print("🧪 Testing SMS sender...")
    result = send_glucose_alert(
        glucose_level=65,
        timestamp="2025-12-17T15:40:00",
        advice="Eat 15g fast-acting carbs. Recheck in 15 minutes."
    )
    print(f"RESULT: {result}")
