# whatsapp_sender.py - FIXED WHATSAPP SENDER
from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_FROM,
    PATIENT_PHONE_WHATSAPP
)

def send_whatsapp_alert(glucose_level, timestamp, advice=""):
    """
    Send WhatsApp alert for abnormal glucose levels
    FIXED: Properly handles string advice
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Determine status with emojis
        if glucose_level <= 70:
            status = "LOW ⚠️"
        elif glucose_level >= 180:
            status = "HIGH ⚠️"
        else:
            status = "OK ✅"
        
        # Format time (HH:MM)
        time_str = timestamp.split('T')[1][:5]
        
        # ✅ CRITICAL FIX: Treat advice as string, not object
        clean_advice = str(advice).strip() if advice else ""
        
        # Build message body
        body = f"🩺 *Glucose Alert* [{status}]\n"
        body += f"🕗 {time_str} | 📏 {glucose_level} mg/dL\n"
        
        if clean_advice:
            body += f"\n💡 *Advice*\n{clean_advice}"
        else:
            # Fallback advice if LLM fails
            if glucose_level <= 70:
                body += "\n💡 *Advice*\nEat 15g fast carbs (juice/tablets). Recheck in 15 min."
            elif glucose_level >= 180:
                body += "\n💡 *Advice*\nHydrate well. Recheck in 1-2 hours."
        
        # Send WhatsApp message
        message = client.messages.create(
            body=body,
            from_=TWILIO_WHATSAPP_FROM,
            to=PATIENT_PHONE_WHATSAPP
        )
        
        return f"✅ WhatsApp sent (SID: {message.sid[:8]}...)"

    except Exception as e:
        error_msg = f"❌ WhatsApp failed: {type(e).__name__} - {str(e)}"
        print(f"🚨 WhatsApp Error: {error_msg}")
        return error_msg

# 🔬 Test function
if __name__ == "__main__":
    print("📲 Testing WhatsApp sender...")
    result = send_whatsapp_alert(
        glucose_level=65,
        timestamp="2025-12-17T14:30:00",
        advice="Eat 15g fast-acting carbs now. Recheck in 15 minutes."
    )
    print(result)
