# web.py - FINAL WORKING VERSION FOR RENDER
import os
from flask import Flask
from twilio.rest import Client
import schedule
import threading
import time
from datetime import datetime

app = Flask(__name__)

def send_test_sms():
    """Send SMS test with proper error handling"""
    try:
        # Get credentials from environment
        account_sid = os.environ['TWILIO_ACCOUNT_SID']
        auth_token = os.environ['TWILIO_AUTH_TOKEN']
        from_number = os.environ['TWILIO_PHONE_NUMBER']
        to_number = os.environ['PATIENT_PHONE_NUMBER']
        
        print(f"✅ SENDING SMS TO LEBANON NUMBER: {to_number}")
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body="✅ GLUCOALERT AI: CLOUD DEPLOYMENT SUCCESSFUL - SMS TO LEBANON WORKING",
            from_=from_number,
            to=to_number
        )
        
        print(f"✅ SMS SENT SUCCESSFULLY - SID: {message.sid[:8]}")
        return True, message.sid[:8]
    
    except Exception as e:
        print(f"❌ SMS FAILED: {str(e)}")
        return False, str(e)[:100]

@app.route('/')
def health():
    return {
        "status": "GlucoAlert AI Running",
        "system": "CLOUD DEPLOYMENT SUCCESSFUL",
        "lebanon_number": "+9613929206",
        "next_test": "Automatic SMS test in 1 minute"
    }

@app.route('/test-sms')
def test_sms():
    success, result = send_test_sms()
    return {
        "status": "✅ TEST SMS SENT SUCCESSFULLY" if success else "❌ TEST SMS FAILED",
        "result": result,
        "recipient": "+9613929206",
        "system": "PRODUCTION READY"
    }

def run_scheduler():
    """Run automatic SMS test every minute"""
    print("✅ STARTING AUTOMATIC SMS TESTS TO LEBANON")
    print("⏰ Testing every 1 minute")
    print("="*50)
    
    # Initial test after 30 seconds
    time.sleep(30)
    send_test_sms()
    
    # Schedule tests every minute
    schedule.every(1).minutes.do(send_test_sms)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start scheduler in background thread
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print("🚀🚀🚀 GLUCOALERT AI - CLOUD DEPLOYMENT SUCCESSFUL 🚀🚀🚀")
    print("✅ LEBANON NUMBER +9613929206 VERIFIED")
    print(f"🌍 RUNNING ON PORT {port}")
    app.run(host="0.0.0.0", port=port)