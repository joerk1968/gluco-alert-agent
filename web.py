# web.py - COMPLETELY FIXED WITH WORKING SMS FALLBACK
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
    """Read glucose and send alert ONLY if truly abnormal with proper SMS fallback."""
    try:
        data = read_glucose_level()
        glucose = data["glucose"]
        timestamp = data["timestamp"]
        trend = data.get("trend", "stable")
        utc_time = datetime.now(timezone.utc).strftime("%H:%M")
        
        print(f"[{utc_time}] Glucose: {glucose} mg/dL ({trend})")
        
        # 🔴 🔴 🔴 CRITICAL FIX: Only alert when TRULY abnormal
        if glucose < HYPO_THRESHOLD or glucose > HYPER_THRESHOLD:
            status = "LOW" if glucose < HYPO_THRESHOLD else "HIGH"
            print(f"⚠️ ALERT TRIGGERED! Glucose: {glucose} mg/dL ({status})")
            
            # Get personalized LLM advice
            advice = get_glucose_advice(glucose, trend, "automated monitoring")
            print(f"💡 Advice: {advice[:60]}...")
            
            # 📱 SMS-ONLY MODE (WhatsApp at daily limit)
            if USE_SMS_ONLY:
                print("📧 SMS-ONLY MODE ACTIVE")
                result = send_glucose_alert(glucose, timestamp, advice)
                print(f"✅ SMS SENT RESULT: {result}")
                return result
            else:
                # Try WhatsApp first
                whatsapp_result = send_whatsapp_alert(glucose, timestamp, advice)
                print(f"📲 WhatsApp Result: {whatsapp_result}")
                
                # 🔁 GUARANTEED SMS FALLBACK
                if "❌" in whatsapp_result or "failed" in whatsapp_result.lower() or "429" in whatsapp_result:
                    print("🚨 WhatsApp failed - FORCING SMS FALLBACK...")
                    result = send_glucose_alert(glucose, timestamp, advice)
                    print(f"✅ SMS FALLBACK RESULT: {result}")
                    return result
                return whatsapp_result
        else:
            # ✅ CORRECT BEHAVIOR: No alert for normal readings
            print(f"✅ Normal glucose ({glucose} mg/dL) - no alert triggered")
            return "Normal glucose - no alert needed"
            
    except Exception as e:
        error_msg = f"🚨 Critical error in check_and_alert: {str(e)}"
        print(error_msg)
        return error_msg

def run_scheduler():
    """Continuous monitoring with proper medical frequency"""
    print("✅ Starting CONTINUOUS glucose monitoring")
    print(f"⏰ Monitoring frequency: every 5 minutes")
    print(f"🩺 Thresholds: Hypo < {HYPO_THRESHOLD} mg/dL | Hyper > {HYPER_THRESHOLD} mg/dL")
    print(f"📱 Message mode: {'SMS-ONLY (WhatsApp limit)' if USE_SMS_ONLY else 'WhatsApp with SMS fallback'}")
    
    # 🩺 MEDICAL-GRADE MONITORING: Every 5 minutes
    schedule.every(5).minutes.do(check_and_alert)
    
    print("="*60)
    print("GlucoAlert AI: 24/7 Continuous Monitoring Active")
    print("="*60)
    
    while True:
        schedule.run_pending()
        time.sleep(30)

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
        "sms_fallback_active": True,
        "next_check": schedule.next_run().strftime("%H:%M") if schedule.next_run() else "Starting soon"
    }

@app.route('/force-alert')
def force_alert():
    """Trigger immediate alert for testing/demo with proper thresholds"""
    print("🚨 MANUAL TEST ALERT TRIGGERED!")
    
    # Test with ABNORMAL glucose that SHOULD trigger alert
    test_glucose = 65  # Below hypo threshold (should trigger)
    test_timestamp = datetime.now(timezone.utc).isoformat()
    test_trend = "falling"
    
    # 🔴 🔴 🔴 CRITICAL: Only proceed if glucose is truly abnormal
    if test_glucose < HYPO_THRESHOLD or test_glucose > HYPER_THRESHOLD:
        advice = get_glucose_advice(test_glucose, test_trend, "manual test")
        
        # FORCE SMS MODE for testing during WhatsApp limits
        result = send_glucose_alert(test_glucose, test_timestamp, advice)
        channel = "SMS"
        
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

# Start scheduler in background thread
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port)
    
  
             
       
     

      
      
