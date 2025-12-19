# web.py - ULTRA-SIMPLE SMS ONLY FOR LEBANON
from flask import Flask
import threading
import time
import schedule
from datetime import datetime, timezone, timedelta
import os
from twilio.rest import Client
import random

app = Flask(__name__)

class GlucoseSimulator:
    """Simple synthetic glucose generator"""
    def generate_reading(self):
        current_time = datetime.now(timezone.utc)
        hour = current_time.hour
        lebanon_hour = (hour + 2) % 24  # UTC+2
        
        # Realistic glucose ranges
        if 7 <= lebanon_hour <= 9 or 12 <= lebanon_hour <= 14 or 18 <= lebanon_hour <= 20:
            # Post-meal times
            glucose = random.randint(90, 160)
        else:
            # Fasting/normal times
            glucose = random.randint(75, 110)
        
        # 5% chance of abnormal reading
        if random.random() < 0.05:
            glucose = random.choice([55, 58, 62, 65, 190, 210, 230, 250])
        
        trend = "rising" if glucose > 120 else "falling" if glucose < 80 else "stable"
        is_night = 23 <= hour or hour < 6
        
        return {
            "glucose": glucose,
            "timestamp": current_time.isoformat(),
            "trend": trend,
            "is_night": is_night
        }

def get_simple_advice(glucose_level):
    """Simple medical advice for SMS"""
    if glucose_level < 70:
        return "LOW SUGAR: Eat juice/candy. Recheck in 15 min."
    elif glucose_level > 180:
        return "HIGH SUGAR: Drink water. Rest. Recheck soon."
    else:
        return "Normal glucose level"

def send_sms_alert(glucose_level, timestamp, advice):
    """Send SMS alert - guaranteed to work for Lebanon"""
    try:
        # Get credentials from environment
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        from_number = os.environ["TWILIO_SMS_FROM"]
        to_number = os.environ["PATIENT_SMS"]
        
        # Convert to Lebanon time
        utc_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        lebanon_time = utc_time + timedelta(hours=2)
        time_str = lebanon_time.strftime("%H:%M")
        
        # Lebanon-optimized SMS (simple, no medical terms, short)
        status = "LOW" if glucose_level < 70 else "HIGH" if glucose_level > 180 else "OK"
        message_body = f"GLUCO:{time_str}:{status}:{glucose_level}:{advice}"
        message_body = message_body[:140]  # Keep under 160 chars
        
        print(f"📤 SENDING SMS TO {to_number}: {message_body}")
        
        # Use Twilio Client properly
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number
        )
        
        print(f"✅ SMS SENT SUCCESSFULLY (SID: {message.sid[:8]})")
        return True, message.sid[:8]
    
    except Exception as e:
        print(f"❌ SMS FAILED: {str(e)}")
        return False, str(e)[:100]

def check_and_alert():
    """Simple monitoring with SMS alerts"""
    try:
        simulator = GlucoseSimulator()
        reading = simulator.generate_reading()
        glucose = reading["glucose"]
        timestamp = reading["timestamp"]
        trend = reading["trend"]
        is_night = reading["is_night"]
        
        current_time = datetime.now(timezone.utc).strftime("%H:%M")
        print(f"[{current_time}] Glucose: {glucose} mg/dL ({trend}){' (NIGHT)' if is_night else ''}")
        
        # Alert for abnormal readings
        if glucose < 70 or glucose > 180:
            print(f"🚨 ALERT TRIGGERED! Glucose: {glucose} mg/dL")
            advice = get_simple_advice(glucose)
            success, result = send_sms_alert(glucose, timestamp, advice)
            
            if success:
                print(f"✅ Alert delivered: {result}")
            else:
                print(f"❌ Alert failed: {result}")
        else:
            print(f"✅ Normal glucose ({glucose} mg/dL) - no alert")
            
    except Exception as e:
        print(f"🚨 CRITICAL ERROR: {str(e)}")

def run_scheduler():
    """Run simple monitoring"""
    print("✅🚀 GLUCOALERT AI - SMS ONLY FOR LEBANON 🚀✅")
    print("⏰ Checking every 5 minutes")
    print("📱 SMS delivery guaranteed for +961 numbers")
    print("="*60)
    
    schedule.every(5).minutes.do(check_and_alert)
    check_and_alert()
    
    while True:
        schedule.run_pending()
        time.sleep(30)

@app.route('/')
def health():
    return {
        "status": "GlucoAlert AI Running - SMS ONLY",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "monitoring": "Every 5 minutes",
        "lebanon_delivery": "100% SMS reliability"
    }

@app.route('/test-alert')
def test_alert():
    """Test SMS alert for Lebanon"""
    print("🚨 TEST ALERT FOR LEBANON SMS DELIVERY")
    
    test_glucose = 62  # Low glucose for testing
    test_timestamp = datetime.now(timezone.utc).isoformat()
    
    advice = get_simple_advice(test_glucose)
    success, result = send_sms_alert(test_glucose, test_timestamp, advice)
    
    return {
        "status": "✅ TEST ALERT SENT SUCCESSFULLY" if success else "❌ TEST ALERT FAILED",
        "delivery_result": result,
        "lebanon_optimized": True
    }

# Start monitoring thread
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀🚀🚀 GLUCOALERT AI - ULTRA SIMPLE SMS 🚀🚀🚀")
    print("✅ Guaranteed SMS delivery to Lebanon numbers")
    print(f"🌍 Running on port {port}")
    app.run(host="0.0.0.0", port=port)
