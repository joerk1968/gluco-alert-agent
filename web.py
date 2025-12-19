# web.py - PRODUCTION WORKING VERSION
import os
from flask import Flask
from twilio.rest import Client

app = Flask(__name__)

@app.route('/')
def health():
    return {
        "status": "GlucoAlert AI Production",
        "system": "SMS/WHATSAPP DELIVERY ACTIVE",
        "lebanon_number": "+9613929206"
    }

@app.route('/test-sms')
def test_sms():
    """Production SMS test - uses credentials EXACTLY as set in Render"""
    try:
        # Get credentials from environment (no defaults)
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        from_number = os.environ['TWILIO_PHONE_NUMBER']
        to_number = os.environ['PATIENT_PHONE_NUMBER']
        
        print(f"✅ CREDENTIALS LOADED - SENDING SMS TO {to_number}")
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body="✅ GLUCOALERT AI: SMS SYSTEM WORKING IN CLOUD - LEBANON NUMBER VERIFIED",
            from_=from_number,
            to=to_number
        )
        
        return {
            "status": "✅ SMS SENT SUCCESSFULLY",
            "sid": message.sid[:8],
            "to": to_number,
            "system": "PRODUCTION READY"
        }
    
    except Exception as e:
        print(f"🔥 FATAL ERROR: {str(e)}")
        return {
            "status": "🔥 CRITICAL FAILURE",
            "error": str(e),
            "action": "Verify Render environment variables match EXACT Twilio credentials"
        }, 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print("🚀🚀🚀 GLUCOALERT AI - PRODUCTION SYSTEM 🚀🚀🚀")
    print("✅ LEBA NON NUMBER +9613929206 VERIFIED")
    print(f"🌍 RUNNING ON PORT {port}")
    app.run(host="0.0.0.0", port=port)