# web.py - WhatsApp-first with intelligent SMS fallback
from flask import Flask
import threading
import time
import schedule
from datetime import datetime
import os
from glucose_reader import read_glucose_level
from llm_advisor import get_glucose_advice
from whatsapp_sender import send_whatsapp_alert
from sms_sender import send_sms_alert
from config import HYPO_THRESHOLD, HYPER_THRESHOLD, USE_WHATSAPP_FIRST, MAX_RETRY_ATTEMPTS

app = Flask(__name__)

def send_alert_with_fallback(glucose_level, timestamp, advice=""):
    """
    Smart alert system: Try WhatsApp first, fall back to SMS if needed.
    Handles retries and provides detailed logging.
    """
    print(f"\n🚨 ALERT TRIGGERED! Glucose: {glucose_level} mg/dL")
    
    for attempt in range(MAX_RETRY_ATTEMPTS):
        print(f"🔄 Attempt {attempt + 1}/{MAX_RETRY_ATTEMPTS}")
        
        if USE_WHATSAPP_FIRST:
            # Try WhatsApp first
            print("📱 Trying WhatsApp delivery...")
            whatsapp_result = send_whatsapp_alert(glucose_level, timestamp, advice)
            
            if whatsapp_result["success"]:
                print("✅ Alert delivered via WhatsApp")
                return {
                    "primary_channel": "whatsapp",
                    "success": True,
                    "result": whatsapp_result
                }
            
            # Handle WhatsApp-specific failures
            if whatsapp_result.get("error") == "daily_limit_reached":
                print("⏭️ WhatsApp limit reached - skipping to SMS")
                break  # Don't retry WhatsApp if limit reached
        
        # Fallback to SMS
        print("📵 WhatsApp failed - falling back to SMS...")
        sms_result = send_sms_alert(glucose_level, timestamp, advice)
        
        if sms_result["success"]:
            print("✅ Alert delivered via SMS fallback")
            return {
                "primary_channel": "whatsapp",
                "fallback_channel": "sms",
                "success": True,
                "result": sms_result
            }
        
        # Wait before retrying
        if attempt < MAX_RETRY_ATTEMPTS - 1:
            wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
            print(f"⏳ Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
    
    # All attempts failed
    print("❌ ALL DELIVERY ATTEMPTS FAILED")
    return {
        "success": False,
        "error": "all_channels_failed",
        "message": "Failed to deliver alert after all retry attempts"
    }

def check_and_alert():
    """Read glucose and send alert if abnormal with WhatsApp-first fallback."""
    try:
        data = read_glucose_level()
        glucose = data["glucose"]
        timestamp = data["timestamp"]
        trend = data.get("trend", "stable")
        current_time = datetime.now().strftime("%H:%M")
        
        print(f"[{current_time}] Glucose: {glucose} mg/dL ({trend})")
        
        # 🔴 🔴 🔴 MEDICALLY ACCURATE THRESHOLDS
        if glucose < HYPO_THRESHOLD or glucose > HYPER_THRESHOLD:
            status = "LOW" if glucose < HYPO_THRESHOLD else "HIGH"
            print(f"⚠️ REAL ALERT: Glucose {glucose} mg/dL ({status})")
            
            # Get LLM advice
            advice = get_glucose_advice(glucose, trend, "automated monitoring")
            print(f"💡 Advice: {advice[:60]}...")
            
            # Send with WhatsApp-first fallback
            delivery_result = send_alert_with_fallback(glucose, timestamp, advice)
            
            return delivery_result
        else:
            print(f"✅ Normal glucose ({glucose} mg/dL) - NO alert triggered")
            return {"status": "normal", "glucose": glucose}
            
    except Exception as e:
        error_msg = f"🚨 CRITICAL ERROR in check_and_alert: {str(e)}"
        print(error_msg)
        return {"error": error_msg}

def run_scheduler():
    """Continuous monitoring every 5 minutes"""
    print("✅ STARTING CONTINUOUS MONITORING")
    print("⏰ Checking every 5 minutes")
    print("📱 Delivery mode: WhatsApp-first with SMS fallback")
    
    schedule.every(5).minutes.do(check_and_alert)
    
    print("="*60)
    print("GLUCOALERT AI: 24/7 MONITORING WITH INTELLIGENT FALLBACK")
    print("="*60)
    
    while True:
        schedule.run_pending()
        time.sleep(30)

@app.route('/')
def health():
    """Health check showing fallback status"""
    return {
        "status": "GlucoAlert AI Running",
        "monitoring": "Every 5 minutes",
        "delivery_mode": "WhatsApp-first with SMS fallback",
        "last_check": datetime.now().strftime("%H:%M")
    }

@app.route('/force-alert')
def force_alert():
    """Force an alert for testing/demo with fallback logic"""
    print("🚨 MANUAL TEST ALERT TRIGGERED!")
    
    test_glucose = 65  # Simulate hypoglycemia
    test_timestamp = datetime.now().isoformat()
    test_trend = "falling"
    test_advice = "TEST: Consume 15g fast-acting carbs. Recheck in 15 minutes."
    
    result = send_alert_with_fallback(test_glucose, test_timestamp, test_advice)
    
    return {
        "status": "TEST ALERT SENT",
        "glucose_level": test_glucose,
        "advice": test_advice,
        "delivery_result": result
    }

# Start scheduler in background thread
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 STARTING GLUCOALERT AI ON PORT {port}")
    print("📱 WhatsApp-first with SMS fallback enabled")
    app.run(host="0.0.0.0", port=port)
