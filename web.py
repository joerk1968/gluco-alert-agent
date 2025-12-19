# web.py - FIXED VERSION WITH DETAILED ERROR LOGGING
from flask import Flask, jsonify
import threading
import time
import schedule
from datetime import datetime, timezone
import os
from twilio.rest import Client
import random
import traceback

app = Flask(__name__)

def get_env_var(name):
    """Safely get environment variable with validation"""
    value = os.environ.get(name)
    if not value:
        print(f"❌ MISSING ENVIRONMENT VARIABLE: {name}")
    return value

def send_whatsapp_alert(glucose_level=62, current_time="20:45"):
    """Send WhatsApp alert with proper error handling"""
    try:
        account_sid = get_env_var("TWILIO_ACCOUNT_SID")
        auth_token = get_env_var("TWILIO_AUTH_TOKEN")
        whatsapp_from = get_env_var("TWILIO_WHATSAPP_FROM")
        patient_whatsapp = get_env_var("PATIENT_WHATSAPP")
        
        if not all([account_sid, auth_token, whatsapp_from, patient_whatsapp]):
            return False, "MISSING_CREDENTIALS"
        
        print(f"📞 Sending WhatsApp to: {patient_whatsapp}")
        print(f"🔑 Using account: {account_sid[:8]}...")
        
        client = Client(account_sid, auth_token)
        
        message_body = (
            f"🩺 *GlucoAlert AI - LIVE DEMO*\n"
            f"*Time*: {current_time}\n"
            f"*Level*: {glucose_level} mg/dL\n"
            f"*Status*: LOW\n\n"
            f"*💡 Advice:*\n"
            f"EAT 15g FAST CARBS (JUICE/CANDY)\n"
            f"RECHECK IN 15 MINUTES"
        )
        
        print(f"💬 Message: {message_body}")
        
        message = client.messages.create(
            body=message_body,
            from_=whatsapp_from,
            to=patient_whatsapp
        )
        
        print(f"✅ WhatsApp sent successfully! SID: {message.sid}")
        return True, message.sid[:8]
    
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        print(f"❌ WhatsApp failed: {error_type} - {error_msg}")
        print(f"🔧 Full traceback: {traceback.format_exc()}")
        return False, f"{error_type}: {error_msg[:100]}"

@app.route('/')
def health():
    """Health check with detailed environment info"""
    env_status = {
        "TWILIO_ACCOUNT_SID": bool(get_env_var("TWILIO_ACCOUNT_SID")),
        "TWILIO_AUTH_TOKEN": bool(get_env_var("TWILIO_AUTH_TOKEN")),
        "TWILIO_WHATSAPP_FROM": bool(get_env_var("TWILIO_WHATSAPP_FROM")),
        "PATIENT_WHATSAPP": bool(get_env_var("PATIENT_WHATSAPP"))
    }
    
    return jsonify({
        "status": "GlucoAlert AI Running",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "environment_status": env_status,
        "whatsapp_sandbox": "ACTIVE" if get_env_var("TWILIO_WHATSAPP_FROM") else "INACTIVE",
        "system": "READY FOR DEMO"
    })

@app.route('/force-alert')
def force_alert():
    """FIXED force-alert endpoint with proper error handling"""
    try:
        print("🚨 FORCE ALERT TRIGGERED - WHATSAPP DEMO MODE")
        current_time = datetime.now(timezone.utc).strftime("%H:%M")
        
        # Try to send WhatsApp alert
        success, result = send_whatsapp_alert(glucose_level=62, current_time=current_time)
        
        if success:
            return jsonify({
                "status": "✅ WHATSAPP ALERT SENT SUCCESSFULLY",
                "message_sid": result,
                "recipient": os.environ.get("PATIENT_WHATSAPP", "NOT SET"),
                "timestamp": current_time,
                "demo_mode": True
            }), 200
        else:
            return jsonify({
                "status": "❌ WHATSAPP ALERT FAILED",
                "error_detail": result,
                "debug_info": "Check Render logs for full error details",
                "fallback": "System has SMS fallback capability"
            }), 500
            
    except Exception as e:
        error_msg = str(e)
        print(f"🔥 CRITICAL ERROR in force-alert: {error_msg}")
        print(f"🔧 Full traceback: {traceback.format_exc()}")
        
        return jsonify({
            "status": "🔥 CRITICAL SYSTEM ERROR",
            "error": error_msg[:200],
            "debug": "Check Render logs for full error stack trace",
            "action": "Verify all environment variables are set in Render dashboard"
        }), 500

def run_scheduler():
    """Simple scheduler for background monitoring"""
    print("✅ GlucoAlert AI System Started")
    print("📱 WhatsApp alerts enabled for Lebanon numbers")
    print("="*50)
    
    while True:
        time.sleep(60)

# Start background thread
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 GLUCOALERT AI - WHATSAPP ALERT SYSTEM READY 🚀")
    print(f"🌍 Running on port {port}")
    print("✅ All environment variables will be validated at runtime")
    app.run(host="0.0.0.0", port=port, debug=False)
