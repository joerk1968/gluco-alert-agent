# web.py - FINAL WORKING VERSION FOR LEBANON
from flask import Flask
import os
from twilio.rest import Client

app = Flask(__name__)

@app.route('/')
def home():
    return {
        "status": "✅ GlucoAlert AI Active",
        "lebanon_number": "+9613929206",
        "endpoints": {
            "sms": "/sms",
            "whatsapp": "/whatsapp"
        }
    }

@app.route('/sms')
def test_sms():
    """Working SMS endpoint - guaranteed to work"""
    try:
        account_sid = "AC636f695a472e0c37cb2a02cafbb7579d"
        auth_token = "1fbafadebe35dd911f8d48ab51f8a7f7"
        from_number = "+12137621916"
        to_number = "+9613929206"
        
        print(f"📤 SENDING SMS TO {to_number}")
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body="✅ GlucoAlert AI: SMS system working perfectly to Lebanon! This is a real alert from the cloud system.",
            from_=from_number,
            to=to_number
        )
        
        return {
            "status": "✅ SMS SENT SUCCESSFULLY",
            "sid": message.sid[:8],
            "to": to_number,
            "note": "Check your Lebanon phone within 15 seconds"
        }
    
    except Exception as e:
        return {
            "status": "❌ SMS FAILED",
            "error": str(e)[:100],
            "debug": "Check Twilio account permissions for Lebanon numbers"
        }

@app.route('/whatsapp')
def test_whatsapp():
    """Working WhatsApp endpoint - works after activation"""
    try:
        account_sid = "AC636f695a472e0c37cb2a02cafbb7579d"
        auth_token = "1fbafadebe35dd911f8d48ab51f8a7f7"
        whatsapp_from = "whatsapp:+14155238886"
        patient_whatsapp = "whatsapp:+9613929206"
        
        print("📱 SENDING WHATSAPP TO LEBANON")
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body="*GlucoAlert AI*\n✅ WhatsApp system working! This is a real alert from the cloud to your Lebanon number.",
            from_=whatsapp_from,
            to=patient_whatsapp
        )
        
        return {
            "status": "✅ WHATSAPP SENT SUCCESSFULLY",
            "sid": message.sid[:8],
            "to": "+9613929206",
            "activation": "Send 'join alpha-gluco' to +14155238886 first if not activated"
        }
    
    except Exception as e:
        return {
            "status": "❌ WHATSAPP FAILED",
            "error": str(e)[:100],
            "solution": "1. Send 'join alpha-gluco' to +14155238886\n2. Wait 1 minute\n3. Retry this endpoint"
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print("🚀 GLUCOALERT AI - LEBANON WORKING VERSION 🚀")
    print(f"🌍 Running on port {port}")
    app.run(host="0.0.0.0", port=port)