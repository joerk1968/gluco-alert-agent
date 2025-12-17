# whatsapp_sender.py - ROBUST WHATSAPP SENDING WITH ERROR HANDLING
import traceback
from twilio.rest import Client
from config import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_FROM,
    PATIENT_PHONE_WHATSAPP
)

def send_whatsapp_alert(glucose_level, timestamp, advice=""):
    """
    Send WhatsApp alert with comprehensive error handling
    """
    try:
        print("📱 Preparing WhatsApp alert...")
        
        # Validate required configuration
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, PATIENT_PHONE_WHATSAPP]):
            raise ValueError("Missing Twilio configuration values")
        
        # Initialize client
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Determine status
        if glucose_level <= 55:
            status = "🚨 CRITICAL LOW"
        elif glucose_level <= 70:
            status = "⚠️ LOW"
        elif glucose_level >= 250:
            status = "🚨 CRITICAL HIGH"
        elif glucose_level >= 180:
            status = "⚠️ HIGH"
        else:
            status = "✅ Normal"
        
        # Format time
        time_str = timestamp.split('T')[1][:5] if 'T' in timestamp else datetime.now(timezone.utc).strftime("%H:%M")
        
        # Prepare advice (handle None/empty)
        clean_advice = str(advice).strip() if advice else ""
        if not clean_advice:
            clean_advice = "No advice available. Please consult your healthcare provider."
        
        # Build message body
        body = f"🩺 *GlucoAlert AI*\n"
        body += f"Status: {status}\n"
        body += f"Time: {time_str} UTC\n"
        body += f"Glucose: {glucose_level} mg/dL\n\n"
        body += f"💡 *Medical Guidance*\n{clean_advice}"
        
        # Truncate if too long (WhatsApp limit ~1000 chars)
        if len(body) > 1200:
            body = body[:1197] + "..."
            print("⚠️ Message truncated to fit WhatsApp limits")
        
        print(f"📤 Sending WhatsApp to {PATIENT_PHONE_WHATSAPP}")
        print(f"   Message preview: {body[:150]}...")
        
        # Send message
        message = client.messages.create(
            body=body,
            from_=TWILIO_WHATSAPP_FROM,
            to=PATIENT_PHONE_WHATSAPP
        )
        
        print(f"✅ WhatsApp sent successfully (SID: {message.sid})")
        return f"✅ WhatsApp sent (SID: {message.sid[:8]}...)"
        
    except Exception as e:
        error_details = traceback.format_exc()
        error_type = type(e).__name__
        
        print(f"❌ WhatsApp sending failed: {error_type}")
        print(f"   Error: {str(e)}")
        print(f"   Details: {error_details[:200]}...")
        
        # Fallback to simplified message if original failed
        try:
            if "critical" in status.lower() or glucose_level <= 70 or glucose_level >= 180:
                fallback_body = (
                    f"🚨 URGENT ALERT\n"
                    f"Glucose: {glucose_level} mg/dL\n"
                    f"Time: {time_str} UTC\n"
                    f"Contact healthcare provider immediately."
                )
                client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                message = client.messages.create(
                    body=fallback_body,
                    from_=TWILIO_WHATSAPP_FROM,
                    to=PATIENT_PHONE_WHATSAPP
                )
                print("✅ Fallback WhatsApp sent successfully")
                return f"✅ Fallback WhatsApp sent (SID: {message.sid[:8]}...)"
        except Exception as fallback_e:
            print(f"❌ Fallback WhatsApp also failed: {type(fallback_e).__name__}")
        
        return f"❌ WhatsApp failed: {error_type} - {str(e)[:100]}"

# 🔬 Test function
if __name__ == "__main__":
    print("📲 Testing WhatsApp sender with error handling...")
    
    # Test successful message
    result = send_whatsapp_alert(
        glucose_level=65,
        timestamp="2025-12-17T14:30:00",
        advice="Consume 15g fast-acting carbs (juice/tablets). Recheck in 15 minutes."
    )
    print(f"✅ Test result: {result}")
    
    # Simulate error test (commented out)
    # result = send_whatsapp_alert(0, "invalid", None)
    # print(f"❌ Error test result: {result}")
