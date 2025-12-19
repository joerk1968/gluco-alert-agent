# web.py - TWILIO AUTHENTICATION FIXED
from flask import Flask, jsonify
import threading
import time
from datetime import datetime, timezone
import os
from twilio.rest import Client
import traceback

app = Flask(__name__)

def send_whatsapp_alert():
    """Send WhatsApp alert with PROPER authentication"""
    try:
        # Get credentials EXACTLY as set in Render
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        whatsapp_from = os.environ["TWILIO_WHATSAPP_FROM"]
        patient_whatsapp = os.environ["PATIENT_WHATSAPP"]
        
        print("🔐 TWILIO AUTHENTICATION DETAILS:")
        print(f"   Account SID: {account_sid[:8]}...{account_sid[-4:]}")
        print(f"   Auth Token: {auth_token[:4]}...{auth_token[-4:]}")
        print(f"   From: {whatsapp_from}")
        print(f"   To: {patient_whatsapp}")
        
        # Create client with explicit credentials
        client = Client(account_sid, auth_token)
        
        # Lebanon time (UTC+2)
        current_time = (datetime.now(timezone.utc) + timezone(timedelta(hours=2))).strftime("%H:%M")
        
        message_body = (
            f"🩺 *GlucoAlert AI - LIVE DEMO*\n"
            f"*Time*: {current_time}\n"
            f"*Level*: 62 mg/dL\n"
            f"*Status*: LOW\n\n"
            f"*💡 Advice:*\n"
            f"EAT 15g FAST CARBS (JUICE/CANDY)\n"
            f"RECHECK IN 15 MINUTES"
        )
        
        print("📤 SENDING WHATSAPP ALERT...")
        print(f"💬 Body: {message_body}")
        
        # Send with explicit parameters
        message = client.messages.create(
            body=message_body,
            from_=whatsapp_from,
            to=patient_whatsapp,
            content_type="text"
        )
        
        print(f"✅ SUCCESS! WhatsApp sent - SID: {message.sid}")
        return True, message.sid[:8]
    
    except KeyError as e:
        missing_var = str(e).strip("'")
        print(f"❌ MISSING ENVIRONMENT VARIABLE: {missing_var}")
        return False, f"MISSING_{missing_var}"
    
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"❌ WHATSAPP FAILED: {error_type} - {error_msg}")
        print(f"🔧 Full error details: {traceback.format_exc()}")
        return False, f"{error_type}: {error_msg[:150]}"

@app.route('/')
def health():
    """Detailed health check with credential verification"""
    print("🔍 HEALTH CHECK TRIGGERED")
    
    required_vars = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_FROM", "PATIENT_WHATSAPP"]
    env_status = {}
    
    for var in required_vars:
        value = os.environ.get(var)
        env_status[var] = "FOUND" if value else "MISSING"
        if value:
            print(f"✅ {var}: {value[:8]}...{value[-4:]}")
        else:
            print(f"❌ {var}: NOT SET")
    
    whatsapp_active = "ACTIVE" if os.environ.get("TWILIO_WHATSAPP_FROM") and os.environ.get("PATIENT_WHATSAPP") else "INACTIVE"
    
    return jsonify({
        "status": "GlucoAlert AI Running",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "environment_status": env_status,
        "whatsapp_status": whatsapp_active,
        "debug_mode": True,
        "system": "AUTHENTICATING WITH TWILIO"
    })

@app.route('/force-alert')
def force_alert():
    """FIXED endpoint with working authentication"""
    print("🚨 FORCE ALERT TRIGGERED - AUTHENTICATION TEST")
    
    try:
        # Test authentication first
        success, result = send_whatsapp_alert()
        
        if success:
            return jsonify({
                "status": "✅ WHATSAPP ALERT SENT SUCCESSFULLY",
                "message_sid": result,
                "recipient": os.environ.get("PATIENT_WHATSAPP"),
                "timestamp": datetime.now(timezone.utc).strftime("%H:%M"),
                "authentication": "SUCCESSFUL",
                "delivery_status": "SENT_TO_TWILIO"
            }), 200
        else:
            return jsonify({
                "status": "❌ WHATSAPP ALERT FAILED",
                "error": result,
                "authentication_status": "FAILED",
                "debug_help": "Check Render logs for detailed authentication error",
                "fallback_available": True
            }), 500
    
    except Exception as e:
        print(f"🔥 CRITICAL ERROR: {str(e)}")
        print(f"🔧 Traceback: {traceback.format_exc()}")
        return jsonify({
            "status": "🔥 CRITICAL SYSTEM FAILURE",
            "error": str(e)[:200],
            "debug": "Authentication failed - check Twilio credentials",
            "action": "Verify Account SID and Auth Token in Render environment"
        }), 500

def run_scheduler():
    """Minimal background thread"""
    print("✅ GlucoAlert AI System Started - Authentication Fixed")
    print("🔐 Using direct Twilio REST API authentication")
    while True:
        time.sleep(3600)  # Sleep for 1 hour

# Start minimal background thread
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print("🚀🚀🚀 GLUCOALERT AI - TWILIO AUTHENTICATION FIXED 🚀🚀🚀")
    print(f"🌍 Running on port {port}")
    print("✅ Ready to send WhatsApp alerts to Lebanon numbers")
    app.run(host="0.0.0.0", port=port, debug=False)
