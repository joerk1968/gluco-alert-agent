# whatsapp_sender.py - WhatsApp messaging with proper error handling
from twilio.rest import Client
import os
import time
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM

def send_whatsapp_alert(glucose_level, timestamp, advice=""):
    """
    Send WhatsApp alert with glucose information and medical advice.
    Returns success status and message SID or error details.
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # Determine status emoji and text
        if glucose_level < 70:
            status_emoji = "⚠️"
            status_text = "LOW"
        elif glucose_level > 180:
            status_emoji = "⚠️"
            status_text = "HIGH"
        else:
            status_emoji = "✅"
            status_text = "OK"
        
        # Format time (remove date part)
        time_str = timestamp.split('T')[1][:5] if 'T' in timestamp else timestamp
        
        # Build WhatsApp message with proper formatting
        message_body = (
            f"🩺 *GlucoAlert AI*\n"
            f"*Status*: {status_emoji} {status_text}\n"
            f"*Time*: {time_str}\n"
            f"*Level*: {glucose_level} mg/dL\n\n"
        )
        
        if advice.strip():
            # Clean advice formatting for WhatsApp
            clean_advice = advice.strip().replace('\n', ' ').replace('  ', ' ')
            message_body += f"*💡 Advice:*\n{clean_advice}"
        
        print(f"📤 SENDING WHATSAPP TO {TWILIO_WHATSAPP_FROM} → {os.getenv('PATIENT_WHATSAPP')}")
        print(f"💬 Message: {message_body[:100]}...")
        
        # Send WhatsApp message
        message = client.messages.create(
            body=message_body,
            from_=TWILIO_WHATSAPP_FROM,
            to=os.getenv("PATIENT_WHATSAPP"),
            persistent_action=[f"tel:{os.getenv('PATIENT_SMS').replace('+', '')}"]
        )
        
        print(f"✅ WHATSAPP SENT SUCCESSFULLY (SID: {message.sid[:8]})")
        return {
            "success": True,
            "channel": "whatsapp",
            "sid": message.sid,
            "status": message.status
        }
    
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        
        print(f"❌ WHATSAPP FAILED: {error_type} - {error_msg}")
        
        # Handle specific Twilio errors
        if "429" in error_msg or "limit" in error_msg.lower():
            print("🚨 WhatsApp daily limit reached - switching to SMS fallback")
            return {
                "success": False,
                "channel": "whatsapp",
                "error": "daily_limit_reached",
                "message": "WhatsApp daily message limit exceeded"
            }
        
        return {
            "success": False,
            "channel": "whatsapp",
            "error": error_type,
            "message": error_msg[:100]  # Truncate long error messages
        }
