# sms_sender.py
from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER,
    PATIENT_PHONE_NUMBER
)

def send_glucose_alert(glucose_level, timestamp, advice=""):
    """
    Sends a carrier-safe SMS alert (minimal, no emojis, short).
    Designed for high deliverability in regions like Lebanon (+961).
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
        
        # Build minimal, carrier-friendly message
        time_str = timestamp.split('T')[1][:5]  # e.g., "14:30"
        message_body = f"[GLUCO] {time_str} | {glucose_level} mg/dL | {status}"
        
        # Add *short* advice — only first sentence, no line breaks
        if advice and advice.strip():
            clean_advice = advice.strip()
            # Take only first sentence (up to first '.', '!', or 80 chars)
            first_sentence = clean_advice.split('.')[0].split('!')[0][:80].strip()
            if first_sentence:
                message_body += f" | {first_sentence}."
        
        # Final safety: truncate to 140 chars (1 SMS segment)
        message_body = message_body[:140]
        
        # Send
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=PATIENT_PHONE_NUMBER
        )
        return f"✅ SMS sent (SID: {message.sid[:8]}...)"
    
    except Exception as e:
        return f"❌ SMS failed: {type(e).__name__}"

# 🔬 Test
if __name__ == "__main__":
    print("🧪 Testing carrier-safe SMS...")
    result = send_glucose_alert(
        glucose_level=65,
        timestamp="2025-12-15T14:30:00",
        advice="Consume 15g fast-acting carbs. Recheck in 15 minutes."
    )
    print(result)