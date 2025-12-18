# web.py - COMPLETE WORKING VERSION
from flask import Flask
import threading
import time
import schedule
from datetime import datetime
import os
from glucose_reader import read_glucose_level
from llm_advisor import get_glucose_advice
from sms_sender import send_glucose_alert

app = Flask(__name__)

def check_and_alert():
    """Read glucose and send alert ONLY if truly abnormal."""
    try:
        data = read_glucose_level()
        glucose = data["glucose"]
        timestamp = data["timestamp"]
        trend = data.get("trend", "stable")
        current_time = datetime.now().strftime("%H:%M")
        
        print(f"[{current_time}] Glucose: {glucose} mg/dL ({trend})")
        
        # 🔴 🔴 🔴 MEDICALLY ACCURATE THRESHOLDS
        if glucose < 70 or glucose > 180:
            status = "LOW" if glucose < 70 else "HIGH"
            print(f"⚠️ REAL ALERT: Glucose {glucose} mg/dL ({status})")
            
            # Get LLM advice
            advice = get_glucose_advice(glucose, trend, "cloud monitoring")
            print(f"💡 Advice: {advice[:60]}...")
            
            # Send SMS alert
            result = send_glucose_alert(glucose, timestamp, advice)
            print(f"✅ SMS RESULT: {result}")
            
            return result
        else:
            print(f"✅ Normal glucose ({glucose} mg/dL) - NO alert triggered")
            return "Normal glucose - no alert"
            
    except Exception as e:
        error_msg = f"🚨 ERROR: {str(e)}"
        print(error_msg)
        return error_msg

def run_scheduler():
    """Continuous monitoring every 5 minutes"""
    print("✅ STARTING CONTINUOUS MONITORING")
    print("⏰ Checking every 5 minutes")
    
    schedule.every(5).minutes.do(check_and_alert)
    
    print("="*50)
    print("GLUCOALERT AI: 24/7 MONITORING ACTIVE")
    print("="*50)
    
    while True:
        schedule.run_pending()
        time.sleep(30)

@app.route('/')
def health():
    return {
        "status": "GlucoAlert AI Running",
        "monitoring": "Every 5 minutes",
        "last_check": datetime.now().strftime("%H:%M")
    }

@app.route('/force-alert')
def force_alert():
    """Force an alert for testing/demo"""
    print("🚨 TEST ALERT: Simulating LOW glucose (65 mg/dL)")
    
    test_glucose = 65
    test_timestamp = datetime.now().isoformat()
    test_trend = "falling"
    
    advice = f"TEST ALERT: Glucose {test_glucose} mg/dL - consume 15g fast-acting carbs"
    result = send_glucose_alert(test_glucose, test_timestamp, advice)
    
    print(f"📤 SMS RESULT: {result}")
    return {
        "status": "TEST ALERT SENT",
        "glucose_level": test_glucose,
        "advice": advice,
        "sms_result": result
    }

# Start scheduler
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 STARTING SERVER ON PORT {port}")
    app.run(host="0.0.0.0", port=port)
