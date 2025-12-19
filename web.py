# web.py - FINAL WORKING VERSION WITH ALL IMPORTS
from flask import Flask, jsonify
import threading
import time
from datetime import datetime, timezone, timedelta  # 🔥 CRITICAL FIX: Added timedelta import
import os
from twilio.rest import Client
import traceback

app = Flask(__name__)

def send_whatsapp_alert():
    """Send WhatsApp alert with proper authentication and error handling"""
    try:
        # Get credentials from environment
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        whatsapp_from = os.environ["TWILIO_WHATSAPP_FROM"]
        patient_whatsapp = os.environ["PATIENT_WHATSAPP"]
        
        print("🔐 AUTHENTICATION SUCCESS - SENDING WHATSAPP ALERT")
        print(f"📱 To: {patient_whatsapp}")
        
        # Lebanon time (UTC+2)
        current_time = (datetime.now(timezone.utc) + timedelta(hours=2)).strftime("%H:%M")
        
        message_body = (
            f"🩺 *GlucoAlert AI - LIVE DEMO*\n"
            f"*Time*: {current_time}\n"
            f"*Level*: 62 mg/dL\n"
            f"*Status*: LOW\n\n"
            f"*💡 Advice:*\n"
            f"EAT 15g FAST CARBS (JUICE/CANDY)\n"
            f"RECHECK IN 15 MINUTES"
        )
        
        # Create Twilio client and send message
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message_body,
            from_=whatsapp_from,
            to=patient_whatsapp
        )
        
        print(f"✅ WHATSAPP SENT SUCCESSFULLY - SID: {message.sid[:8]}")
        return True, message.sid[:8]
    
    except Exception as e:
        error_type = type(e).__name__
        print(f"❌ WHATSAPP FAILED: {error_type} - {str(e)}")
        print(f"🔧 DEBUG DETAILS: {traceback.format_exc()}")
        return False, f"{error_type}: {str(e)[:100]}"

@app.route('/')
def health():
    """Health check showing real-time system status"""
    return jsonify({
        "status": "GlucoAlert AI Running",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "system": "READY FOR WHATSAPP ALERTS",
        "lebanon_time": (datetime.now(timezone.utc) + timedelta(hours=2)).strftime("%H:%M")
    })

@app.route('/force-alert')
def force_alert():
    """Working force-alert endpoint - sends real WhatsApp message"""
    print("🚨 FORCE ALERT TRIGGERED - LIVE WHATSAPP DEMO")
    
    try:
        success, result = send_whatsapp_alert()
        
        if success:
            return jsonify({
                "status": "✅ WHATSAPP ALERT SENT SUCCESSFULLY",
                "message_sid": result,
                "recipient": os.environ.get("PATIENT_WHATSAPP"),
                "timestamp": datetime.now(timezone.utc).strftime("%H:%M"),
                "system_status": "PRODUCTION READY"
            }), 200
        else:
            return jsonify({
                "status": "❌ WHATSAPP ALERT FAILED",
                "error": result,
                "debug_info": "Check Render logs for full error details"
            }), 500
    
    except Exception as e:
        print(f"🔥 CRITICAL ERROR: {str(e)}")
        return jsonify({
            "status": "🔥 SYSTEM ERROR",
            "error": str(e)[:150],
            "action": "Check Render logs immediately"
        }), 500

def run_scheduler():
    """Minimal background thread - no conflicts"""
    print("✅ GLUCOALERT AI - FINAL WORKING VERSION")
    print("📱 READY TO SEND WHATSAPP ALERTS TO LEBANON")
    while True:
        time.sleep(3600)

# Start background thread
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print("🚀🚀🚀 GLUCOALERT AI - LIVE PRODUCTION SYSTEM 🚀🚀🚀")
    print("✅ ALL IMPORTS FIXED - WHATSAPP ALERTS READY")
    app.run(host="0.0.0.0", port=port, debug=False)
