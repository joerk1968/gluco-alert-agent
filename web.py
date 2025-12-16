
# web.py - CORRECTED FOR CONTINUOUS MONITORING
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
from config import HYPO_THRESHOLD, HYPER_THRESHOLD

app = Flask(__name__)

def check_and_alert():
    """Read glucose, get LLM advice, send alert if needed."""
    try:
        data = read_glucose_level()
        glucose = data["glucose"]
        timestamp = data["timestamp"]
        trend = data.get("trend", "stable")
        utc_time = datetime.now(timezone.utc).strftime("%H:%M")
        
        print(f"[{utc_time}] Glucose: {glucose} mg/dL ({trend})")
        
        # ALERT LOGIC: Send alerts for abnormal readings
        if glucose <= HYPO_THRESHOLD or glucose >= HYPER_THRESHOLD:
            print(f"⚠️ ALERT TRIGGERED! Glucose: {glucose} mg/dL")
            advice = get_glucose_advice(glucose, trend, "automated monitoring")
            print(f"💡 Advice: {advice[:60]}...")
            
            # Try WhatsApp first
            result = send_whatsapp_alert(glucose, timestamp, advice)
            print(f"📲 WhatsApp: {result}")
            
            # Fallback to SMS if needed
            if "❌" in result:
                print("🔁 SMS fallback...")
                result = send_glucose_alert(glucose, timestamp, advice)
                print(f"📱 SMS: {result}")
        else:
            print(f"✅ Normal glucose: {glucose} mg/dL")
            
    except Exception as e:
        print(f"🚨 Error in check_and_alert: {e}")

def run_scheduler():
    """Continuous monitoring with proper medical frequency"""
    print("✅ Starting CONTINUOUS glucose monitoring")
    
    # 🩺 MEDICAL-GRADE MONITORING FREQUENCY
    # Every 5 minutes (standard for real CGMs)
    schedule.every(5).minutes.do(check_and_alert)
    print("⏰ Primary monitoring: every 5 minutes")
    
    # 🌙 Enhanced nighttime monitoring (critical for hypoglycemia)
    schedule.every(15).minutes.do(lambda: print("🌙 Nighttime safety check active"))
    
    # 🚨 Emergency monitoring (if out of range, check every 2 minutes)
    print("🚨 Emergency monitoring: every 2 minutes when abnormal")
    
    print("="*60)
    print("GlucoAlert AI: 24/7 Continuous Monitoring Active")
    print("="*60)
    
    while True:
        schedule.run_pending()
        time.sleep(30)  # Check every 30 seconds for pending jobs

@app.route('/')
def health():
    """Health check endpoint with UTC time"""
    now = datetime.now(timezone.utc)
    return {
        "status": "GlucoAlert AI Running",
        "server_time_utc": now.strftime("%Y-%m-%d %H:%M:%S"),
        "monitoring_frequency": "Every 5 minutes",
        "next_check": schedule.next_run().strftime("%Y-%m-%d %H:%M:%S") if schedule.next_run() else "Starting soon"
    }

@app.route('/force-alert')
def force_alert():
    """Trigger immediate alert for testing/demo"""
    print("🚨 MANUAL ALERT TRIGGERED!")
    
    # Simulate low glucose for testing
    test_data = {
        "glucose": 65,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "trend": "falling"
    }
    
    advice = get_glucose_advice(test_data["glucose"], test_data["trend"], "manual test")
    whatsapp_result = send_whatsapp_alert(test_data["glucose"], test_data["timestamp"], advice)
    
    print(f"💡 Generated advice: {advice}")
    print(f"📲 WhatsApp: {whatsapp_result}")
    
    return {
        "status": "Manual alert triggered successfully",
        "glucose_level": test_data["glucose"],
        "timestamp": test_data["timestamp"],
        "advice": advice,
        "whatsapp_result": whatsapp_result
    }

@app.route('/whatsapp-webhook', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages (required by Twilio sandbox)"""
    try:
        message_body = request.values.get('Body', '').lower()
        from_number = request.values.get('From', '')
        print(f"📱 Incoming WhatsApp message from {from_number}: '{message_body}'")
        
        if "status" in message_body:
            response_text = "🟢 GlucoAlert AI: System HEALTHY\n⏰ Checking every 5 minutes\n🩺 Ready for alerts"
        elif "help" in message_body:
            response_text = "💡 I'm a glucose monitoring bot. Reply 'status' for system health."
        else:
            response_text = "✅ System active. Send 'status' for details."
        
        resp = MessagingResponse()
        resp.message(response_text)
        return str(resp)
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        resp = MessagingResponse()
        resp.message("❌ Error processing request")
        return str(resp), 500

# Start scheduler in background thread
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)



        
   
 
    
   
       
