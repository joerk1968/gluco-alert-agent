# web.py - WHATSAPP WORKING FOR LEBANON +961
import os
from flask import Flask
from twilio.rest import Client

app = Flask(__name__)

@app.route('/')
def health():
    return {
        "status": "GlucoAlert AI - WHATSAPP READY",
        "lebanon_number": "+9613929206",
        "whatsapp_status": "ACTIVATION REQUIRED"
    }

@app.route('/test-whatsapp')
def test_whatsapp():
    """Test WhatsApp with Lebanon-specific formatting"""
    try:
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        whatsapp_from = "whatsapp:+14155238886"  # Twilio sandbox number
        patient_whatsapp = "whatsapp:+9613929206"  # Lebanon number
        
        print("📱 TESTING WHATSAPP TO LEBANON...")
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body="*GlucoAlert AI*\nHello from Lebanon! This test proves WhatsApp delivery works to +961 numbers when properly configured.",
            from_=whatsapp_from,
            to=patient_whatsapp
        )
        
        return {
            "status": "✅ WHATSAPP TEST INITIATED",
            "sid": message.sid[:8],
            "to": "+9613929206",
            "note": "Check WhatsApp in 15-60 seconds. Lebanon delivery may take longer due to carrier processing."
        }
    
    except Exception as e:
        error_msg = str(e)
        print(f"❌ WHATSAPP FAILED: {error_msg}")
        
        # Lebanon-specific error handling
        if "403" in error_msg or "forbidden" in error_msg.lower():
            return {
                "status": "❌ WHATSAPP FAILED - LEBANON RESTRICTION",
                "error": error_msg,
                "solution": "1. Verify Lebanon number in Twilio Console\n2. Enable Lebanon geo-permissions\n3. Reset sandbox and retry join alpha-gluco"
            }
        
        if "401" in error_msg or "authenticate" in error_msg.lower():
            return {
                "status": "❌ WHATSAPP FAILED - AUTHENTICATION",
                "error": error_msg,
                "solution": "1. Check Twilio credentials\n2. Ensure WhatsApp sandbox is properly configured"
            }
        
        return {
            "status": "❌ WHATSAPP FAILED",
            "error": error_msg[:100],
            "debug": "Check Twilio console for Lebanon messaging permissions"
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print("🚀 GLUCOALERT AI - WHATSAPP FOR LEBANON READY 🚀")
    print("📱 SEND 'join alpha-gluco' TO +14155238886 ON WHATSAPP")
    app.run(host="0.0.0.0", port=port)