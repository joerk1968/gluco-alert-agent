# web.py - FIXED WITH BASE64 IMPORT
from flask import Flask
import threading
import time
import schedule
from datetime import datetime, timezone, timedelta
import os
import random
import requests
from urllib.parse import quote
import base64  # 🔥 CRITICAL FIX: Add base64 import

app = Flask(__name__)

class GlucoseSimulator:
    """Realistic synthetic glucose generator"""
    def __init__(self):
        self.base_glucose = 95
        self.last_meal_time = time.time() - 7200
    
    def generate_reading(self):
        current_time = datetime.now(timezone.utc)
        hour = current_time.hour
        is_night = 23 <= hour or hour < 6
        lebanon_hour = (hour + 2) % 24
        
        meal_effect = 0
        if (7 <= lebanon_hour <= 9) or (12 <= lebanon_hour <= 14) or (18 <= lebanon_hour <= 20):
            if time.time() - self.last_meal_time > 3600:
                self.last_meal_time = time.time()
                meal_effect = random.uniform(30, 80)
        
        base = self.base_glucose + random.uniform(-10, 15)
        if is_night:
            base -= random.uniform(5, 15)
        
        glucose = base + meal_effect
        glucose = max(40, min(400, glucose))
        
        trend = "rising" if meal_effect > 20 else "falling" if is_night and random.random() < 0.3 else "stable"
        
        if random.random() < 0.05:
            glucose = 55 + random.randint(0, 10) if random.random() < 0.5 else 190 + random.randint(0, 30)
        
        return {
            "glucose": round(glucose, 1),
            "timestamp": current_time.isoformat(),
            "trend": trend,
            "is_night": is_night
        }

def get_llm_advice(glucose_level, trend, is_night=False):
    """Generate concise, safe medical advice"""
    if glucose_level < 70:
        return "LOW BLOOD SUGAR: Eat 15g fast carbs (juice/candy). Wait 15 min, recheck. Get help if worse."
    elif glucose_level > 180:
        return "HIGH BLOOD SUGAR: Drink water, rest. Recheck in 1-2 hours. Call doctor if >250 mg/dL."
    else:
        return "Glucose normal - keep monitoring."

def send_alert(glucose_level, timestamp, advice, trend, is_night):
    """Send alert with proper authentication and Lebanon fallback"""
    try:
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        
        if not account_sid or not auth_token:
            return False, "Missing Twilio credentials"
        
        # Convert to Lebanon time
        utc_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        lebanon_time = utc_time + timedelta(hours=2)
        time_str = lebanon_time.strftime("%H:%M")
        
        # Lebanon-optimized message
        status = "LOW" if glucose_level < 70 else "HIGH" if glucose_level > 180 else "OK"
        simple_advice = advice[:50].replace('\n', ' ').replace('•', '-').strip()
        
        # Setup authentication headers
        auth_header = f"Basic {base64.b64encode((account_sid + ':' + auth_token).encode()).decode()}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": auth_header
        }
        
        # Try SMS first (more reliable for Lebanon)
        sms_from = os.environ.get("TWILIO_SMS_FROM", "+12137621916")
        patient_sms = os.environ.get("PATIENT_SMS", "+9613929206")
        
        sms_body = f"GLUCO:{time_str}:{status}:{glucose_level}:{simple_advice}"
        sms_body = sms_body[:140]  # SMS character limit
        
        try:
            data = {
                "Body": sms_body,
                "From": sms_from,
                "To": patient_sms
            }
            
            response = requests.post(
                f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json",
                data=data,
                headers=headers,
                timeout=15
            )
            
            if response.status_code == 201:
                print(f"✅ SMS sent successfully (HTTP {response.status_code})")
                return True, f"SMS:{response.json().get('sid', '')[:8]}"
            else:
                print(f"❌ SMS failed (HTTP {response.status_code}): {response.text}")
                return False, f"HTTP {response.status_code}"
        
        except Exception as e:
            print(f"❌ SMS exception: {str(e)}")
            return False, str(e)[:100]
    
    except Exception as e:
        print(f"❌ Alert failed: {str(e)}")
        return False, str(e)[:100]

def check_and_alert():
    """Continuous monitoring with Lebanon-optimized SMS"""
    try:
        simulator = GlucoseSimulator()
        reading = simulator.generate_reading()
        glucose = reading["glucose"]
        timestamp = reading["timestamp"]
        trend = reading["trend"]
        is_night = reading["is_night"]
        
        current_time = datetime.now(timezone.utc).strftime("%H:%M")
        print(f"[{current_time}] Glucose: {glucose} mg/dL ({trend}){' (NIGHT)' if is_night else ''}")
        
        if glucose < 70 or glucose > 180:
            print(f"🚨 ALERT TRIGGERED! Glucose: {glucose} mg/dL")
            advice = get_llm_advice(glucose, trend, is_night)
            success, result = send_alert(glucose, timestamp, advice, trend, is_night)
            
            if success:
                print(f"✅ Alert delivered: {result}")
            else:
                print(f"❌ Alert failed: {result}")
        else:
            print(f"✅ Normal glucose ({glucose} mg/dL) - no alert")
            
    except Exception as e:
        print(f"🚨 CRITICAL ERROR: {str(e)}")

def run_scheduler():
    """Run continuous monitoring"""
    print("✅🚀 GLUCOALERT AI - SMS FIRST FOR LEBANON 🚀✅")
    print("⏰ Checking every 5 minutes")
    print("📱 SMS delivery optimized for Lebanon carriers")
    print("="*60)
    
    schedule.every(5).minutes.do(check_and_alert)
    check_and_alert()
    
    while True:
        schedule.run_pending()
        time.sleep(30)

@app.route('/')
def health():
    return {
        "status": "GlucoAlert AI Running - SMS FIRST",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "monitoring": "Every 5 minutes",
        "lebanon_delivery": "SMS optimized"
    }

@app.route('/test-alert')
def test_alert():
    """Test alert with Lebanon-optimized SMS delivery"""
    print("🚨 TEST ALERT FOR LEBANON SMS DELIVERY")
    
    test_glucose = 62
    test_timestamp = datetime.now(timezone.utc).isoformat()
    test_trend = "falling"
    test_is_night = False
    
    advice = get_llm_advice(test_glucose, test_trend, test_is_night)
    success, result = send_alert(test_glucose, test_timestamp, advice, test_trend, test_is_night)
    
    return {
        "status": "✅ TEST ALERT SENT SUCCESSFULLY" if success else "❌ TEST ALERT FAILED",
        "delivery_result": result,
        "lebanon_optimized": True
    }

# Start monitoring
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀🚀🚀 GLUCOALERT AI - LEBANON SMS OPTIMIZED 🚀🚀🚀")
    print("✅ SMS delivery prioritized for Lebanon reliability")
    app.run(host="0.0.0.0", port=port)
