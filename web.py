# web.py - FIXED WITH OS IMPORT
import os  # 🔥 CRITICAL FIX: Added os import
from flask import Flask
import threading
import time
import schedule
from datetime import datetime
from glucose_reader import read_glucose_level
from sms_sender import send_sms_alert
from config import LOW_GLUCOSE, HIGH_GLUCOSE

app = Flask(__name__)

def check_and_alert():
    """Read glucose and send alert if abnormal"""
    try:
        data = read_glucose_level()
        glucose = data["glucose"]
        timestamp = data["timestamp"]
        
        current_time = datetime.now().strftime("%H:%M")
        print(f"[{current_time}] Glucose: {glucose:.1f} mg/dL")
        
        # Alert only for truly abnormal readings
        if glucose < LOW_GLUCOSE or glucose > HIGH_GLUCOSE:
            print(f"🚨 ALERT TRIGGERED! Glucose: {glucose:.1f} mg/dL")
            
            if glucose < LOW_GLUCOSE:
                advice = "LOW SUGAR: Eat 15g fast carbs. Recheck in 15 min."
            else:
                advice = "HIGH SUGAR: Drink water. Rest. Recheck soon."
            
            print(f"💡 Advice: {advice}")
            
            # Send SMS alert
            success, result = send_sms_alert(glucose, timestamp, advice)
            
            if success:
                print(f"✅ Alert delivered: {result}")
            else:
                print(f"❌ Alert failed: {result}")
        else:
            print(f"✅ Normal glucose ({glucose:.1f} mg/dL) - no alert")
            
    except Exception as e:
        print(f"🚨 SYSTEM ERROR: {str(e)}")

def run_scheduler():
    """Run monitoring every 5 minutes"""
    print("✅ GLUCOALERT AI STARTED - SMS ALERTS TO LEBANON")
    print("⏰ Checking every 5 minutes")
    print("📱 SMS delivery to +9613929206")
    print("="*50)
    
    schedule.every(5).minutes.do(check_and_alert)
    
    # Run initial check
    check_and_alert()
    
    while True:
        schedule.run_pending()
        time.sleep(30)

@app.route('/')
def health():
    return {
        "status": "GlucoAlert AI Running",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "monitoring": "Every 5 minutes"
    }

@app.route('/test-sms')
def test_sms():
    """Test SMS endpoint - guaranteed to work"""
    print("🚨 TEST SMS TRIGGERED")
    
    # Send test SMS
    success, result = send_sms_alert(
        glucose_level=62,
        timestamp=datetime.now().isoformat(),
        advice="TEST ALERT: System working in cloud"
    )
    
    return {
        "status": "✅ TEST SMS SENT SUCCESSFULLY" if success else "❌ TEST SMS FAILED",
        "delivery_result": result,
        "recipient": "+9613929206"
    }

# Start scheduler in background thread
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 STARTING GLUCOALERT AI ON PORT {port}")
    print("✅ READY FOR CLOUD DEPLOYMENT")
    app.run(host="0.0.0.0", port=port)