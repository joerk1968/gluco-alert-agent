# whatsapp_sender.py - FINAL FIXED VERSION
from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_FROM,
    PATIENT_PHONE_WHATSAPP
)

def send_whatsapp_alert(glucose_level, timestamp, advice=""):
    """
    Sends alert via WhatsApp with proper string handling.
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        status = "⚠️ LOW" if glucose_level <= 70 else "⚠️ HIGH" if glucose_level >= 180 else "✅ Normal"
        time_str = timestamp.split('T')[1][:5]  # e.g., "14:30"
        
        # ✅ CRITICAL: Handle advice as plain string, NO .get() calls
        clean_advice = str(advice).strip() if advice else ""
        
        body = f"🩺 Glucose Alert [{status}]\nTime: {time_str}\nLevel: {glucose_level} mg/dL"
        
        if clean_advice:
            body += f"\n\n💡 Advice:\n{clean_advice}"
        else:
            if glucose_level <= 70:
                body += "\n\n💡 Quick fix:\nEat 15g fast carbs (e.g., 4 oz juice). Recheck in 15 min."
            elif glucose_level >= 180:
                body += "\n\n💡 Suggestion:\nHydrate, consider light activity. Recheck in 1–2 hours."

        # Send SMS
        message = client.messages.create(
            body=body.strip(),
            from_=TWILIO_WHATSAPP_FROM,
            to=PATIENT_PHONE_WHATSAPP
        )
        return f"✅ WhatsApp sent (SID: {message.sid[:8]}...)"

    except Exception as e:
        error_msg = f"❌ WhatsApp failed: {type(e).__name__}: {str(e)}"
        print(f"🚨 WhatsApp Error: {error_msg}")
        return error_msg

# 🔬 Test
if __name__ == "__main__":
    print("📲 Testing WhatsApp sender...")
    result = send_whatsapp_alert(
        glucose_level=65,
        timestamp="2025-12-17T06:49:06.456548+00:00",
        advice="Eat 15g fast-acting carbs now. Avoid driving until >70 mg/dL."
    )
    print(result)
