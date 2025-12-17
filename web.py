# web.py - COMPLETELY FIXED VERSION
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import threading
import time
import schedule
from datetime import datetime, timezone
import os
from glucose_reader import read_glucose_level
from llm_advisor import get_glucose_advice
from whatsapp_sender import send_whatsapp_alert
from sms_sender import send_glucose_alert
from config import HYPO_THRESHOLD, HYPER_THRESHOLD, USE_SMS_ONLY

app = Flask(__name__)

def check_and_alert():
    """Read glucose, get LLM advice, send alert ONLY if truly abnormal."""
    try:
        data = read_glucose_level()
        glucose = data["glucose"]
        timestamp = data["timestamp"]
        trend = data.get("trend", "stable")
        utc_time = datetime.now(timezone.utc).strftime("%H:%M")
        
        print(f"[{utc_time}] Glucose: {glucose} mg/dL ({trend})")
        
        # 🔴 🔴 🔴 CRITICAL FIX: Only alert when TRULY abnormal
      # ✅ MEDICALLY ACCURATE THRESHOLDS:
if glucose < HYPO_THRESHOLD or glucose > HYPER_THRESHOLD:
    # Only trigger for truly abnormal readings
    print(f"⚠️ REAL ALERT: Glucose {glucose} mg/dL is abnormal")
    # ... rest of alert logic
else:
    print(f"✅ Normal glucose ({glucose} mg/dL) - NO alert triggered")
    return  # Exit function without sending any message
            
            # 📱 Use SMS-only mode since WhatsApp is at daily limit
            if USE_SMS_ONLY:
                print("📧 SMS-ONLY MODE (WhatsApp limit reached)")
                result = send_glucose_alert(glucose, timestamp, advice)
                print(f"📱 SMS Result: {result}")
            else:
                # Try WhatsApp first
                whatsapp_result = send_whatsapp_alert(glucose, timestamp, advice)
                print(f"📲 WhatsApp Result: {whatsapp_result}")
                
                # 🔁 FALLBACK TO SMS IF WHATSAPP FAILS
                if "❌" in whatsapp_result or "failed" in whatsapp_result.lower():
                    print("🔁 WhatsApp failed - falling back to SMS...")
                    result = send_glucose_alert(glucose, timestamp, advice)
                    print(f"📱 SMS Fallback Result: {result}")
                else:
                    result = whatsapp_result
        else:
            # ✅ CORRECT BEHAVIOR: No alert for normal readings
            print(f"✅ Normal glucose ({glucose} mg/dL) - no alert triggered")
            
    except Exception as e:
        print(f"🚨 Critical error in check_and_alert: {e}")
        import traceback
        print(traceback.format_exc())

def run_scheduler():
    """Continuous monitoring with proper medical frequency"""
    print("✅ Starting CONTINUOUS glucose monitoring")
    print(f"⏰ Monitoring frequency: every 5 minutes")
    print(f"🩺 Thresholds: Hypo < {HYPO_THRESHOLD} mg/dL | Hyper > {HYPER_THRESHOLD} mg/dL")
    print(f"📱 Message mode: {'SMS-ONLY (WhatsApp limit)' if USE_SMS_ONLY else 'WhatsApp with SMS fallback'}")
    
    # 🩺 MEDICAL-GRADE MONITORING: Every 5 minutes
    schedule.every(5).minutes.do(check_and_alert)
    
    # 🌙 Extra safety check for overnight hours
    schedule.every().day.at("22:00").do(lambda: print("🌙 Nighttime safety protocol active"))
    
    print("="*60)
    print("GlucoAlert AI: 24/7 Continuous Monitoring Active")
    print("="*60)
    
    while True:
        schedule.run_pending()
        time.sleep(30)  # Check every 30 seconds for pending jobs

@app.route('/')
def health():
    """Enhanced health check with system status"""
    now = datetime.now(timezone.utc)
    return {
        "status": "GlucoAlert AI Running",
        "server_time_utc": now.strftime("%Y-%m-%d %H:%M:%S"),
        "monitoring_frequency": "Every 5 minutes",
        "thresholds": {
            "hypo": HYPO_THRESHOLD,
            "hyper": HYPER_THRESHOLD
        },
        "message_mode": "SMS-ONLY (limit reached)" if USE_SMS_ONLY else "WhatsApp + SMS fallback",
        "next_check": schedule.next_run().strftime("%H:%M") if schedule.next_run() else "Starting soon"
    }

@app.route('/force-alert')
def force_alert():
    """Trigger immediate alert for testing/demo with PROPER thresholds"""
    print("🚨 MANUAL ALERT TRIGGERED!")
    
    # Test with ABNORMAL glucose that SHOULD trigger alert
    test_glucose = 65  # Below hypo threshold (should trigger)
    # test_glucose = 185  # Above hyper threshold (should trigger)
    # test_glucose = 92  # Normal (should NOT trigger)
    # Before generating advice, check if glucose is truly abnormal
test_glucose = 101.9  # This should NOT trigger an alert
if test_glucose >= HYPO_THRESHOLD and test_glucose <= HYPER_THRESHOLD:
    return {
        "status": "NO ALERT TRIGGERED - NORMAL GLUCOSE",
        "glucose_level": test_glucose,
        "advice": "Glucose is within normal range (70-180 mg/dL). No action needed."
    }
    test_timestamp = datetime.now(timezone.utc).isoformat()
    test_trend = "falling"
    
    # 🔴 🔴 🔴 CRITICAL: Only proceed if glucose is truly abnormal
    if test_glucose < HYPO_THRESHOLD or test_glucose > HYPER_THRESHOLD:
        advice = get_glucose_advice(test_glucose, test_trend, "manual test")
        
        if USE_SMS_ONLY:
            result = send_glucose_alert(test_glucose, test_timestamp, advice)
            channel = "SMS"
        else:
            result = send_whatsapp_alert(test_glucose, test_timestamp, advice)
            channel = "WhatsApp"
            
            # Fallback if needed
            if "❌" in result:
                result = send_glucose_alert(test_glucose, test_timestamp, advice)
                channel = "SMS (fallback)"
        
        print(f"💡 Generated advice: {advice}")
        print(f"📤 {channel} result: {result}")
        
        return {
            "status": "Manual alert triggered successfully",
            "glucose_level": test_glucose,
            "timestamp": test_timestamp,
            "advice": advice,
            "channel_used": channel,
            "result": result
        }
    else:
        # ✅ CORRECT BEHAVIOR: No alert for normal readings
        advice = "No alert needed - glucose is within normal range."
        print(f"✅ Normal glucose ({test_glucose} mg/dL) - no alert triggered")
        return {
            "status": "No alert triggered - normal glucose level",
            "glucose_level": test_glucose,
            "timestamp": test_timestamp,
            "advice": advice,
            "channel_used": "none"
        }

@app.route('/whatsapp-webhook', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages (required by Twilio sandbox)"""
    try:
        message_body = request.values.get('Body', '').lower()
        from_number = request.values.get('From', '')
        print(f"📱 Incoming WhatsApp message from {from_number}: '{message_body}'")
        
        if "status" in message_body or "hello" in message_body:
            response_text = (
                "🟢 GlucoAlert AI: System HEALTHY\n"
                f"⏰ Monitoring: every 5 minutes\n"
                f"🩺 Thresholds: <{HYPO_THRESHOLD} or >{HYPER_THRESHOLD} mg/dL\n"
                f"📱 Mode: {'SMS-only' if USE_SMS_ONLY else 'WhatsApp+SMS'}"
            )
        elif "help" in message_body:
            response_text = (
                "💡 GlucoAlert AI monitors your glucose levels 24/7.\n"
                "When levels are abnormal, you'll receive personalized advice.\n"
                "Reply 'status' for system health."
            )
        else:
            response_text = "✅ System active. Reply 'status' for details."
        
        resp = MessagingResponse()
        resp.message(response_text)
        return str(resp)
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        resp = MessagingResponse()
        resp.message("❌ System error - please try again later")
        return str(resp), 500

# Start scheduler in background thread
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 10000))  # Render's default port is 10000
    print(f"🚀 Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port)
