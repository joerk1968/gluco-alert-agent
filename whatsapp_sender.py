# whatsapp_sender.py
from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_FROM,
    PATIENT_PHONE_WHATSAPP
)

def send_whatsapp_alert(glucose_level, timestamp, advice=""):
    """
    Sends alert via WhatsApp (more reliable in Lebanon).
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        status = "⚠️ LOW" if glucose_level <= 70 else "⚠️ HIGH" if glucose_level >= 180 else "✅ OK"
        time_str = timestamp.split('T')[1][:5]
        
        body = (
            f"🩺 *Glucose Alert* [{status}]\n"
            f"🕗 {time_str} | 📏 {glucose_level} mg/dL\n"
        )
        if advice.strip():
            body += f"\n💡 *Advice*\n{advice}"
        else:
            body += "\n💡 Check your levels."

        message = client.messages.create(
            body=body,
            from_=TWILIO_WHATSAPP_FROM,
            to=PATIENT_PHONE_WHATSAPP,
            persistent_action=[f"tel:{PATIENT_PHONE_WHATSAPP.replace('whatsapp:', '')}"]
        )
        return f"✅ WhatsApp sent (SID: {message.sid[:8]}...)"
    
    except Exception as e:
        return f"❌ WhatsApp failed: {e}"

# 🔬 Test
if __name__ == "__main__":
    print("📲 Testing WhatsApp...")
    result = send_whatsapp_alert(
        glucose_level=65,
        timestamp="2025-12-15T14:30:00",
        advice="Eat 15g fast-acting carbs (e.g., juice). Recheck in 15 min."
    )
    print(result)