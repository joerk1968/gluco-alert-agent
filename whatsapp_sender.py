 # whatsapp_sender.py - FIXED FOR STRING-BASED ADVICE
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
    Fixed to properly handle string-based LLM advice.
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Determine status (short: LOW/HIGH/OK)
        if glucose_level <= 70:
            status = "LOW ⚠️"
        elif glucose_level >= 180:
            status = "HIGH ⚠️"
        else:
            status = "OK ✅"
        
        # Format time (remove date part)
        time_str = timestamp.split('T')[1][:5]  # e.g., "14:30"
        
        # Build message body - handle advice as string, not dictionary
        body = f"🩺 *Glucose Alert* [{status}]\n"
        body += f"🕗 {time_str} | 📏 {glucose_level} mg/dL\n"
        
        # Add advice if provided (handle as string, not object)
        if advice and isinstance(advice, str) and advice.strip():
            # Clean up advice: remove extra whitespace and ensure proper formatting
            clean_advice = advice.strip()
            # If advice contains error messages, show them but don't crash
            if "error" in clean_advice.lower() or "exception" in clean_advice.lower():
                body += f"\n🚨 *Error in advice generation*:\n{clean_advice}"
            else:
                body += f"\n💡 *Advice*\n{clean_advice}"
        else:
            # Fallback advice based on glucose level
            if glucose_level <= 70:
                body += "\n💡 *Advice*\nEat 15g fast-acting carbs (e.g., juice). Recheck in 15 min."
            elif glucose_level >= 180:
                body += "\n💡 *Advice*\nHydrate and consider light activity. Recheck in 1-2 hours."
            else:
                body += "\n💡 Glucose in normal range."
        
        # Ensure message doesn't exceed WhatsApp limits
        if len(body) > 1000:  # WhatsApp has limits on message length
            body = body[:997] + "..."
        
        # Send the message
        message = client.messages.create(
            body=body,
            from_=TWILIO_WHATSAPP_FROM,
            to=PATIENT_PHONE_WHATSAPP,
            persistent_action=[f"tel:{PATIENT_PHONE_WHATSAPP.replace('whatsapp:', '')}"]
        )
        return f"✅ WhatsApp sent (SID: {message.sid[:8]}...)"
    
    except Exception as e:
        error_msg = f"❌ WhatsApp failed: {type(e).__name__}: {str(e)}"
        print(f"🚨 WhatsApp Error: {error_msg}")
        return error_msg

# 🔬 Test
if __name__ == "__main__":
    print("📲 Testing WhatsApp...")
    result = send_whatsapp_alert(
        glucose_level=65,
        timestamp="2025-12-16T19:52:45.134602+00:00",
        advice="The patient should eat or drink something with fast-acting carbohydrates, like fruit juice or glucose tablets, to raise their blood sugar. It's important to stay hydrated by drinking water. After 15 minutes, they should recheck their blood sugar; if it's still low or they feel unwell, seek help immediately."
    )
    print(result)
