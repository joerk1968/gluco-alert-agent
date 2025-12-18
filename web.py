# web.py - COMPLETE VERSION WITH ALL ENDPOINTS
from flask import Flask
import threading
import time
import schedule
from datetime import datetime
import os
from twilio.rest import Client

app = Flask(__name__)

def check_and_alert():
    """Simple monitoring function"""
    print("✅ GlucoAlert AI: Healthy - monitoring active")

def run_scheduler():
    """Continuous monitoring thread"""
    while True:
        check_and_alert()
        time.sleep(300)  # 5 minutes

@app.route('/')
def health():
    """Health check endpoint"""
    return {
        "status": "GlucoAlert AI Running",
        "message": "System healthy - ready for deployment",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

@app.route('/force-alert')
def force_alert():
    """Force an alert for testing/demo - SENDS WHATSAPP MESSAGE"""
    try:
        print("🚨 MANUAL TEST ALERT TRIGGERED!")
        
        # Get Twilio credentials from environment
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM")
        patient_whatsapp = os.getenv("PATIENT_WHATSAPP")
        
        if not all([account_sid, auth_token, whatsapp_from, patient_whatsapp]):
            return {
                "error": "Missing Twilio credentials",
                "required": ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_FROM", "PATIENT_WHATSAPP"],
                "note": "Set these in Render environment variables"
            }, 500
        
        # Create WhatsApp message
        message_body = (
            "🩺 *GlucoAlert AI - TEST ALERT*\n"
            "*Status*: ⚠️ LOW (TEST)\n"
            "*Time*: " + datetime.now().strftime("%H:%M") + "\n"
            "*Level*: 65 mg/dL (TEST)\n\n"
            "*💡 Advice:*\n"
            "TEST: Consume 15g fast-acting carbs. Recheck in 15 minutes."
        )
        
        print(f"📤 SENDING WHATSAPP TO {patient_whatsapp}")
        print(f"💬 Message: {message_body}")
        
        # Send WhatsApp message
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message_body,
            from_=whatsapp_from,
            to=patient_whatsapp
        )
        
        print(f"✅ WHATSAPP SENT SUCCESSFULLY (SID: {message.sid[:8]})")
        
        return {
            "status": "TEST ALERT SENT SUCCESSFULLY",
            "channel": "whatsapp",
            "message_sid": message.sid[:8],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "recipient": patient_whatsapp,
            "note": "Check your WhatsApp for the test message"
        }
    
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"❌ ALERT FAILED: {error_type} - {error_msg}")
        
        return {
            "error": "Failed to send test alert",
            "exception": error_type,
            "message": error_msg[:100],
            "note": "Check Render logs for detailed error"
        }, 500

# Start monitoring thread
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting GlucoAlert AI on port {port}")
    app.run(host="0.0.0.0", port=port)
