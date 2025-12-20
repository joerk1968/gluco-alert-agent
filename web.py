# web.py - SIMPLEST WORKING VERSION WITH GUARANTEED URLS
from flask import Flask
import os
from twilio.rest import Client

app = Flask(__name__)

@app.route('/')
def home():
    """Main page - always works"""
    return {
        "status": "✅ GlucoAlert AI Active",
        "message": "System running - use /sms or /whatsapp endpoints"
    }

@app.route('/sms')
def test_sms():
    """Simple SMS test endpoint - guaranteed to work"""
    try:
        # Hardcoded credentials for testing
        account_sid = "AC636f695a472e0c37cb2a02cafbb7579d"
        auth_token = "1fbafadebe35dd911f8d48ab51f8a7f7"
        from_number = "+12137621916"
        to_number = "+9613929206"
        
        print(f"📤 SENDING TEST SMS TO {to_number}")
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body="✅ TEST: GlucoAlert AI system working - SMS delivery successful",
            from_=from_number,
            to=to_number
        )
        
        return {
            "status": "✅ SMS TEST SENT SUCCESSFULLY",
            "sid": message.sid[:8],
            "to": to_number,
            "note": "Check your Lebanon phone within 15 seconds"
        }
    
    except Exception as e:
        return {
            "status": "❌ SMS TEST FAILED",
            "error": str(e)[:100],
            "solution": "1. Verify Twilio account has Lebanon permissions\n2. Check if number +9613929206 is verified in Twilio Console"
        }

@app.route('/whatsapp')
def test_whatsapp():
    """Simple WhatsApp test endpoint"""
    try:
        account_sid = "AC636f695a472e0c37cb2a02cafbb7579d"
        auth_token = "1fbafadebe35dd911f8d48ab51f8a7f7"
        whatsapp_from = "whatsapp:+14155238886"
        patient_whatsapp = "whatsapp:+9613929206"
        
        print("📱 SENDING TEST WHATSAPP")
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body="*GlucoAlert AI*\n✅ Test message - WhatsApp delivery working to Lebanon",
            from_=whatsapp_from,
            to=patient_whatsapp
        )
        
        return {
            "status": "✅ WHATSAPP TEST SENT",
            "sid": message.sid[:8],
            "to": "+9613929206",
            "note": "Must send 'join alpha-gluco' to +14155238886 first to activate"
        }
    
    except Exception as e:
        return {
            "status": "❌ WHATSAPP TEST FAILED",
            "error": str(e)[:100],
            "activation": "Send 'join alpha-gluco' to +14155238886 on WhatsApp first"
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print("🚀 GLUCOALERT AI - MINIMAL WORKING VERSION 🚀")
    print(f"🌍 Running on port {port}")
    print("✅ URLs: /  |  /sms  |  /whatsapp")
    app.run(host="0.0.0.0", port=port)