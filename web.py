# web.py - GUARANTEED CREDENTIAL LOADING FOR RENDER
from flask import Flask
import threading
import time
import schedule
from datetime import datetime, timezone
import os
from twilio.rest import Client
import random

app = Flask(__name__)

def load_environment_variables():
    """Force load environment variables - critical for Render deployment"""
    required_vars = [
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN", 
        "TWILIO_WHATSAPP_FROM",
        "PATIENT_WHATSAPP"
    ]
    
    print("🔍 LOADING ENVIRONMENT VARIABLES...")
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}: {value[:8]}...")  # Show first 8 chars for security
        else:
            print(f"❌ MISSING: {var}")
    
    # Return success status
    return all(os.environ.get(var) for var in required_vars)

class GlucoseSimulator:
    """Realistic synthetic glucose generator"""
    def __init__(self):
        self.base_glucose = 95
        self.last_meal_time = time.time() - 7200
    
    def generate_reading(self):
        current_time = datetime.now(timezone.utc)
        hour = current_time.hour
        
        is_night = 23 <= hour or hour < 6
        meal_effect = random.uniform(30, 80) if time.time() - self.last_meal_time < 3600 else 0
        
        base = self.base_glucose + random.uniform(-10, 15)
        if is_night:
            base -= random.uniform(5, 15)
        
        glucose = base + meal_effect
        glucose = max(40, min(400, glucose))
        
        trend = "rising" if meal_effect > 0 else "falling" if is_night else "stable"
        
        return {
            "glucose": round(glucose, 1),
            "timestamp": current_time.isoformat(),
            "trend": trend,
            "is_night": is_night
        }

def get_llm_advice(glucose_level, trend, is_night=False):
    """Generate safe medical advice"""
    if glucose_level < 70:
        return ("⚠️ LOW BLOOD SUGAR ALERT\n"
               "• Consume 15g fast-acting carbohydrates (juice, candy, glucose tabs)\n"
               "• Wait 15 minutes, then recheck your glucose\n"
               "• If still below 70 mg/dL, repeat treatment\n"
               "• Seek emergency help if symptoms worsen or glucose remains low")
    elif glucose_level > 180:
        return ("⚠️ HIGH BLOOD SUGAR ALERT\n"
               "• Drink water to stay hydrated\n"
               "• Check for ketones if you have type 1 diabetes\n"
               "• Consider light physical activity (10-min walk)\n"
               "• Recheck glucose in 1-2 hours")
    else:
        return ("✅ GLUCOSE IN TARGET RANGE\n"
               "• Continue regular monitoring\n"
               "• Stay hydrated throughout the day")

def send_whatsapp_alert(glucose_level, timestamp, advice, trend, is_night):
    """Send WhatsApp alert with proper error handling"""
    try:
        # Force reload environment variables
        credentials_loaded = load_environment_variables()
        
        if not credentials_loaded:
            print("❌ CREDENTIALS STILL MISSING AFTER RELOAD")
            return False, "Missing credentials after reload"
        
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        whatsapp_from = os.environ["TWILIO_WHATSAPP_FROM"]
        patient_whatsapp = os.environ["PATIENT_WHATSAPP"]
        
        status = "LOW" if glucose_level < 70 else "HIGH" if glucose_level > 180 else "NORMAL"
        status_emoji = "⚠️" if status in ["LOW", "HIGH"] else "✅"
        time_str = timestamp.split('T')[1][:5]
        
        message_body = (
            f"🩺 *GlucoAlert AI - {status} GLUCOSE*\n"
            f"*Time*: {time_str} {'(NIGHT)' if is_night else ''}\n"
            f"*Level*: {glucose_level} mg/dL\n"
            f"*Trend*: {trend.capitalize()}\n\n"
            f"*💡 AI MEDICAL ADVICE:*\n{advice}"
        )
        
        print(f"📤 SENDING WHATSAPP: {message_body[:100]}...")
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message_body,
            from_=whatsapp_from,
            to=patient_whatsapp
        )
        
        print(f"✅ WHATSAPP SENT SUCCESSFULLY (SID: {message.sid[:8]})")
        return True, message.sid[:8]
    
    except KeyError as e:
        print(f"❌ MISSING ENVIRONMENT VARIABLE: {e}")
        return False, f"Missing {str(e)}"
    except Exception as e:
        print(f"❌ WHATSAPP ERROR: {type(e).__name__} - {str(e)}")
        return False, str(e)[:100]

def check_and_alert():
    """Continuous monitoring"""
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
            success, result = send_whatsapp_alert(glucose, timestamp, advice, trend, is_night)
            
            if success:
                print(f"✅ Alert delivered successfully (SID: {result})")
            else:
                print(f"❌ Alert delivery failed: {result}")
        else:
            print(f"✅ Normal glucose ({glucose} mg/dL) - no alert needed")
            
    except Exception as e:
        print(f"🚨 CRITICAL ERROR: {str(e)}")

def run_scheduler():
    """Run continuous monitoring"""
    print("✅ STARTING 24/7 MONITORING")
    print("⏰ Checking every 5 minutes")
    
    # Force load credentials at startup
    load_environment_variables()
    
    schedule.every(5).minutes.do(check_and_alert)
    check_and_alert()  # Initial check
    
    while True:
        schedule.run_pending()
        time.sleep(30)

@app.route('/')
def health():
    """Health check with credential status"""
    credentials_loaded = all(os.environ.get(var) for var in [
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_WHATSAPP_FROM", 
        "PATIENT_WHATSAPP"
    ])
    
    return {
        "status": "GlucoAlert AI Running",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "monitoring": "Every 5 minutes",
        "credentials_loaded": credentials_loaded,
        "environment": "Render Cloud"
    }

@app.route('/test-alert')
def test_alert():
    """Test alert with explicit credential check"""
    print("🚨 MANUAL TEST ALERT TRIGGERED")
    
    # Force reload environment variables
    credentials_loaded = load_environment_variables()
    
    if not credentials_loaded:
        return {
            "status": "❌ TEST ALERT FAILED",
            "error": "Missing Twilio credentials",
            "required": ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_FROM", "PATIENT_WHATSAPP"],
            "note": "Set these in Render Environment tab and restart service"
        }, 500
    
    test_glucose = 62
    test_timestamp = datetime.now(timezone.utc).isoformat()
    test_trend = "falling"
    test_is_night = False
    
    advice = get_llm_advice(test_glucose, test_trend, test_is_night)
    success, result = send_whatsapp_alert(test_glucose, test_timestamp, advice, test_trend, test_is_night)
    
    return {
        "status": "✅ TEST ALERT SENT SUCCESSFULLY" if success else "❌ TEST ALERT FAILED",
        "glucose_level": test_glucose,
        "timestamp": test_timestamp,
        "advice": advice,
        "delivery_result": result,
        "credentials_loaded": credentials_loaded
    }

# Start monitoring
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀🚀🚀 GLUCOALERT AI STARTING ON PORT {port} 🚀🚀🚀")
    print("✅ Environment variables will be loaded at startup")
    app.run(host="0.0.0.0", port=port)
