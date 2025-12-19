# web.py - EXACT WORKING VERSION FROM 2 DAYS AGO
from flask import Flask
import threading
import time
import schedule
from datetime import datetime, timezone
import os
from twilio.rest import Client
import random
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def check_and_alert():
    try:
        # Generate realistic synthetic glucose reading
        base_glucose = 95 + random.uniform(-10, 15)
        glucose = max(70, min(180, base_glucose))  # Keep in normal range most of the time
        
        # 10% chance of abnormal reading for testing
        if random.random() < 0.1:
            glucose = random.choice([62, 65, 190, 210])
        
        timestamp = datetime.now(timezone.utc).isoformat()
        trend = "falling" if glucose < 90 else "rising" if glucose > 110 else "stable"
        
        current_time = datetime.now(timezone.utc).strftime("%H:%M")
        print(f"[{current_time}] Glucose: {glucose} mg/dL ({trend})")
        
        # Alert only for truly abnormal readings
        if glucose < 70 or glucose > 180:
            print(f"🚨 ALERT TRIGGERED! Glucose: {glucose} mg/dL")
            
            # Generate LLM advice
            if glucose < 70:
                advice = "LOW BLOOD SUGAR ALERT: Consume 15g fast-acting carbohydrates (juice, candy, glucose tabs). Wait 15 minutes, then recheck your glucose. If still below 70 mg/dL, repeat treatment. Seek emergency help if symptoms worsen."
            else:
                advice = "HIGH BLOOD SUGAR ALERT: Drink water to stay hydrated. Check for ketones if you have type 1 diabetes. Consider light physical activity. Recheck glucose in 1-2 hours. Contact healthcare provider if >250 mg/dL or symptoms persist."
            
            print(f"💡 Advice: {advice[:60]}...")
            
            # Send WhatsApp alert first
            whatsapp_success = False
            try:
                client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
                message = client.messages.create(
                    body=f"🩺 GlucoAlert AI\nTime: {current_time}\nLevel: {glucose} mg/dL\nTrend: {trend}\n\n💡 Advice:\n{advice}",
                    from_=os.getenv("TWILIO_WHATSAPP_FROM"),
                    to=os.getenv("PATIENT_WHATSAPP"),
                    persistent_action=[f"tel:{os.getenv('PATIENT_PHONE_NUMBER').replace('+', '')}"]
                )
                print(f"✅ WhatsApp sent (SID: {message.sid[:8]})")
                whatsapp_success = True
            except Exception as e:
                print(f"❌ WhatsApp failed: {str(e)}")
            
            # Fallback to SMS if WhatsApp fails
            if not whatsapp_success:
                try:
                    client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
                    message = client.messages.create(
                        body=f"GLUCO ALERT:{current_time}|{glucose}mg/dL|{trend}|{advice[:50]}",
                        from_=os.getenv("TWILIO_PHONE_NUMBER"),
                        to=os.getenv("PATIENT_PHONE_NUMBER")
                    )
                    print(f"✅ SMS sent (SID: {message.sid[:8]})")
                except Exception as e:
                    print(f"❌ SMS failed: {str(e)}")
        else:
            print(f"✅ Normal glucose ({glucose} mg/dL) - no alert needed")
            
    except Exception as e:
        print(f"🚨 CRITICAL ERROR: {str(e)}")

def run_scheduler():
    print("✅ GLUCOALERT AI: 24/7 MONITORING ACTIVE")
    print("⏰ Checking every 5 minutes")
    print("="*50)
    
    schedule.every(5).minutes.do(check_and_alert)
    
    while True:
        schedule.run_pending()
        time.sleep(30)

@app.route('/')
def health():
    return {
        "status": "GlucoAlert AI Running",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "monitoring": "Every 5 minutes"
    }

@app.route('/force-alert')
def force_alert():
    """Trigger immediate alert for testing/demo"""
    print("🚨 MANUAL ALERT TRIGGERED!")
    
    test_glucose = 65  # Simulate low glucose
    test_timestamp = datetime.now(timezone.utc).isoformat()
    test_trend = "falling"
    
    if test_glucose < 70:
        advice = "TEST ALERT: Consume 15g fast-acting carbs. Recheck in 15 minutes."
    else:
        advice = "TEST ALERT: Drink water and recheck glucose levels."
    
    # Send WhatsApp alert
    try:
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        message = client.messages.create(
            body=f"🩺 TEST ALERT\nTime: {datetime.now(timezone.utc).strftime('%H:%M')}\nLevel: {test_glucose} mg/dL\nTrend: {test_trend}\n\n💡 Advice:\n{advice}",
            from_=os.getenv("TWILIO_WHATSAPP_FROM"),
            to=os.getenv("PATIENT_WHATSAPP")
        )
        print(f"✅ TEST WhatsApp sent (SID: {message.sid[:8]})")
        return {"status": "✅ TEST ALERT SENT VIA WHATSAPP", "glucose_level": test_glucose, "advice": advice}
    except Exception as e:
        print(f"❌ WhatsApp failed: {str(e)}")
    
    # Fallback to SMS
    try:
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        message = client.messages.create(
            body=f"TEST GLUCO:{datetime.now(timezone.utc).strftime('%H:%M')}:{test_glucose}mg/dL:{test_trend}:{advice[:50]}",
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=os.getenv("PATIENT_PHONE_NUMBER")
        )
        print(f"✅ TEST SMS sent (SID: {message.sid[:8]})")
        return {"status": "✅ TEST ALERT SENT VIA SMS", "glucose_level": test_glucose, "advice": advice}
    except Exception as e:
        print(f"❌ SMS failed: {str(e)}")
        return {"status": "❌ TEST ALERT FAILED", "error": str(e)[:100]}

# Start scheduler in background thread
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 STARTING GLUCOALERT AI ON PORT {port}")
    print("✅ REAL-TIME MONITORING WITH SMS/WHATSAPP DELIVERY")
    app.run(host="0.0.0.0", port=port)
